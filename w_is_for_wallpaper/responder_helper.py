"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved

Adapter to mysql/business logic related to data schemes module (repacking queries/replies)
"""

import datetime
import hashlib
from w_is_for_wallpaper import mysqlpools as pools
from w_is_for_wallpaper import devices
from w_is_for_wallpaper import dict_repacker
from w_is_for_wallpaper import history
from w_is_for_wallpaper import entities
from w_is_for_wallpaper import mysql_db_themes_images
from w_is_for_wallpaper import responder


def get_coords_by_id_device_type(image_id, device_type):
    return pools.db_themes_images.get_image_coords_by_id_device_type(image_id, device_type)


def get_all_coords_by_id(image_id):
    return {'desktop': pools.db_themes_images.get_image_coords_by_id_device_type(image_id, devices.DeviceType.desktop),
            'cellphone': pools.db_themes_images.get_image_coords_by_id_device_type(image_id, devices.DeviceType.cellphone),
            'band': pools.db_themes_images.get_image_coords_by_id_device_type(image_id, devices.DeviceType.band)}


def image_reply_repack(image_info):
    return dict_repacker.repack({'id': 'id',
                                 'thumbnail': 'thumbnail', 'source': 'source', 'categories': 'categories',
                                 'license': 'license', 'colors_matched': 'colors_matched',
                                 'resolution': {'width': 'width', 'height': 'height'},
                                 'uid': 'uid', 'mtime': 'mtime',
                                 'origin': 'origin', 'votes': 'votes'},
                                image_info)


def image_query_repack(image_dict):
    return dict_repacker.repack({'thumbnail': 'thumbnail', 'source': 'source', 'categories': 'categories',
                                 'license': 'license', 'colors_matched': 'colors_matched',
                                 'width': 'resolution:width', 'height': 'resolution:height',
                                 'uid': 'uid', 'origin': 'origin', 'votes': 'votes'},
                                image_dict)


def category_query_repack(category_dict):
    return dict_repacker.repack({'name': 'name', 'image_id_cover': 'image_id_cover'}, category_dict)


def category_reply_repack(category_info):
    return dict_repacker.repack({'name': 'name', 'id': 'id', 'image_id_cover': 'image_id_cover'}, category_info)


def history_reply_repack(history_info):
    return dict_repacker.repack({'id': 'id', 'event_type': 'event_type', 'entity_type': 'entity_type',
                                 'entity_id': 'entity_id', 'date': 'date'}, history_info)


def get_responder_proxy(ids, entity_type):
    entity_to_db_themes_images_function_mapping = {
        entities.EntityTypes.image: pools.db_themes_images.get_images,
        entities.EntityTypes.license: pools.db_themes_images.get_licenses,
        entities.EntityTypes.category: pools.db_themes_images.get_categories
    }
    entity_to_repackers = {
        entities.EntityTypes.image: image_reply_repack,
        entities.EntityTypes.category: category_reply_repack
    }
    entity_to_amount = {
        entities.EntityTypes.image: 20000,
        entities.EntityTypes.license: None,
        entities.EntityTypes.category: None
    }
    amount = None
    if ids is not None and not isinstance(ids, list):  # if we were asked with a list, we'll return a list of dicts
        ids_list = [ids]
    else:
        if ids is None:
            amount = entity_to_amount[entity_type]
        ids_list = ids
    if amount is None:
        res = entity_to_db_themes_images_function_mapping[entity_type](ids_list)
    else:
        res = entity_to_db_themes_images_function_mapping[entity_type](ids_list, amount=amount)
    if not res:
        return []
    res_repacked = (list(map(entity_to_repackers[entity_type], res))
                    if entity_type in entity_to_repackers else res)

    if ids is not None and not isinstance(ids, list):  # if we were asked with a single id, we'll return a dict
        res_repacked = res_repacked[0]

    return res_repacked


# IMAGE FUNCTIONS


def get_images(image_ids):
    return get_responder_proxy(image_ids, entities.EntityTypes.image)


def get_random_image(orientation, category_id, color_id):
    try:
        image_id = pools.db_themes_images.get_random_image_id(orientation, category_id, color_id)['id']
    except (KeyError, AttributeError, TypeError):
        return None
    return get_responder_proxy(image_id, entities.EntityTypes.image)


def get_images_full_info_by_category_id(category_id):
    images_info = pools.db_themes_images.get_images_full_info_by_category(category_id)
    images_info_repacked = list(map(image_reply_repack, images_info))
    return images_info_repacked


def get_image_info_with_coords_by_id_device_type(image_id, device_type):
    image_info = pools.db_themes_images.get_image_info_by_id(image_id)
    image_info['coords'] = get_coords_by_id_device_type(image_id, device_type)
    return image_info


def get_newest_images_count_by_category(category_ids, since_date):
    if category_ids:
        return {'count': pools.db_themes_images.get_newest_images_count_by_category(category_ids, since_date)[
            'count(distinct image_id)']}
    else:
        return {'count': pools.db_themes_images.get_newest_images_count(since_date)[
            'count(distinct image_id)']}

# def get_images_full_info_newest(amount):
#     images_info = pools.db_themes_images.get_images_full_info_newest(amount)
#     images_info_repacked = list(map(image_reply_repack, images_info))
#     return images_info_repacked


def post_image(image_data):
    image_data_repacked = image_query_repack(image_data)
    category_ids = image_data_repacked.pop('categories')
    try:
        if len(get_categories(category_ids)) != len(category_ids):
            return None
    except TypeError:
        return None

    color_ids = image_data_repacked.pop('colors_matched')
    try:
        if len(get_colors(color_ids)) != len(color_ids):
            return None
    except TypeError:
        return None
    if not ('uid' in image_data_repacked):
        image_data_repacked['uid'] = hashlib.md5(image_data_repacked['source'].encode()).hexdigest()
    image_data_repacked['mtime'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    lastid = pools.db_themes_images.add_image(image_data_repacked)
    pools.db_themes_images.add_category_image_mapping(category_ids, lastid)
    pools.db_themes_images.add_color_image_mapping(color_ids, lastid)
    pools.db_themes_images.recalculate_image_top(lastid)
    # pools.db_themes_images.add_image_top_coefficient(lastid, None)  # TODO
    return {'id': lastid}


def get_themes_full_info():
    themes_info = pools.db_themes_images.get_themes_full_info()
    return themes_info


def delete_images(image_ids):
    if not isinstance(image_ids, list):
        image_ids = [image_ids]
    if len(get_images(image_ids)) != len(image_ids):
        return None

    pools.db_themes_images.delete_dailies_entries_by_images(image_ids)
    # categories_with_dailies = pools.db_themes_images.get_categories_images_are_daily_for(image_ids)
    # if categories_with_dailies:
    #     raise responder.ResponderException('Could not delete some images. Some are dailies. {}'.format(
    #         categories_with_dailies
    #     ))
    categories_with_covers = pools.db_themes_images.get_categories_images_are_cover_for(image_ids)
    if categories_with_covers:
        raise responder.ResponderException('Could not delete some images. Some are covers. {}'.format(
            categories_with_covers
        ))

    current_categories_ids = [x['category_id'] for x in get_categories_mapping(image_ids)]
    current_color_ids = [x['color_id'] for x in get_colors_mapping(image_ids)]
    pools.db_themes_images.delete_category_image_mapping(current_categories_ids, image_ids)
    pools.db_themes_images.delete_color_image_mapping(current_color_ids, image_ids)
    # pools.db_themes_images.delete_images_top_coefficient(image_ids)  # TODO
    res = pools.db_themes_images.delete_images(image_ids)

    return res


def get_categories_mapping(image_ids):
    return pools.db_themes_images.get_categories_mapping(image_ids)


def get_colors_mapping(image_ids):
    return pools.db_themes_images.get_colors_mapping(image_ids)


def modify_image(image_id, image_data):
    image_data_repacked = image_query_repack(image_data)

    try:
        category_ids = image_data_repacked.pop('categories', [])
        if category_ids and len(get_categories(category_ids)) != len(category_ids):
            return None

        color_ids = image_data_repacked.pop('colors_matched', [])
        if color_ids and len(get_colors(color_ids)) != len(color_ids):
            return None
    except TypeError:
        return None

    if not ('uid' in image_data_repacked) and 'source' in image_data_repacked:
        image_data_repacked['uid'] = hashlib.md5(image_data_repacked['source'].encode()).hexdigest()

    if not get_images(image_id):
        return None
    res = [None]

    # image_data_repacked['mtime'] = datetime.datetime.utcnow()  # TODO review ;we probably don't need it
                                                                # so we have rough info whether the image is old or not

    if image_data_repacked:
        res = pools.db_themes_images.modify_image(image_id, image_data_repacked)

    if category_ids:
        current_categories_ids_set = set([x['category_id'] for x in get_categories_mapping(image_id)])
        category_ids_set = set(category_ids)
        categories_ids_to_remove = list(current_categories_ids_set - category_ids_set)
        categories_ids_to_add = list(category_ids_set - current_categories_ids_set)
        pools.db_themes_images.delete_category_image_mapping(categories_ids_to_remove, image_id)
        pools.db_themes_images.add_category_image_mapping(categories_ids_to_add, image_id)

    if color_ids:
        current_color_ids_set = [x['color_id'] for x in get_colors_mapping(image_id)]
        pools.db_themes_images.delete_color_image_mapping(current_color_ids_set, image_id)
        pools.db_themes_images.add_color_image_mapping(color_ids, image_id)

    return res


def image_vote(image_id, votes_amount):
    res = pools.db_themes_images.modify_image_votes(image_id, votes_amount)
    return res


def get_image_top(amount):
    res = [x['id'] for x in pools.db_themes_images.get_image_top(amount)]
    return res


def recalculate_image_top():
    res = pools.db_themes_images.recalculate_images_top()
    return res


# CATEGORY FUNCTIONS

def get_categories(cat_id=None):
    return get_responder_proxy(cat_id, entities.EntityTypes.category)


def post_category(category_data):
    category_data_repacked = category_query_repack(category_data)
    return {'id': pools.db_themes_images.add_category(category_data_repacked)}


def delete_categories(category_ids):
    if not isinstance(category_ids, list):
        category_ids = [category_ids]
    if len(get_categories(category_ids)) != len(category_ids):
        return None
    pools.db_themes_images.delete_dailies_entries_by_categories(category_ids)
    return pools.db_themes_images.delete_categories(category_ids)


def modify_category(category_id, category_data):
    category_data_repacked = category_query_repack(category_data)
    if not get_categories(category_id):
        return None
    return pools.db_themes_images.modify_category(category_id, category_data_repacked)


def get_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_before_date):
    image_id = pools.db_themes_images.get_daily_image_id(category_id, daily_image_type, daily_image_orientation,
                                                         daily_image_before_date)
    if not image_id:
        return None
    image_info = get_images(image_id)
    return image_info


def delete_daily_image(category_id, daily_image_type, daily_image_orientation):
    res = pools.db_themes_images.delete_daily_image(category_id, daily_image_type, daily_image_orientation)
    return res


def modify_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_data):
    res = pools.db_themes_images.modify_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_data)
    return res


# COLOR FUNCTIONS

def get_colors(color_id=None):
    return pools.db_themes_images.get_colors(color_id)


def post_color(color_data):
    return {'id': pools.db_themes_images.add_color(color_data)}


def delete_colors(color_ids):
    if not isinstance(color_ids, list):
        color_ids = [color_ids]
    if len(get_colors(color_ids)) != len(color_ids):
        return None
    return pools.db_themes_images.delete_colors(color_ids)


def modify_color(color_id, color_data):
    if not get_colors(color_id):
        return None
    return pools.db_themes_images.modify_color(color_id, color_data)


# LICENSE FUNCTIONS

def get_licenses(license_ids):
    return get_responder_proxy(license_ids, entities.EntityTypes.license)


def post_license(license_data):
    return {'id': pools.db_themes_images.add_license(license_data)}


def delete_licenses(license_ids):
    if not isinstance(license_ids, list):
        license_ids = [license_ids]
    if len(get_licenses(license_ids)) != len(license_ids):
        return None
    return pools.db_themes_images.delete_licenses(license_ids)


def modify_license(license_id, license_data):
    if not get_licenses(license_id):
        return None
    return pools.db_themes_images.modify_license(license_id, license_data)


# HISTORY FUNCTIONS

def get_history(since_date, entity_type):
    entity_type_to_get_info_function = {
        entities.EntityTypes.category: get_categories,
        entities.EntityTypes.color: get_colors,
        entities.EntityTypes.license: get_licenses,
        entities.EntityTypes.image: get_images,
        entities.EntityTypes.theme: get_themes_full_info
    }

    history_data = pools.db_themes_images.get_history(since_date, entity_type)
    if entity_type == entities.EntityTypes.everything:  # raw history for everything
        res = list(map(history_reply_repack, history_data))
    else:
        try:
            last_event_date = history_data[-1]['date']
        except IndexError:
            last_event_date = None
        entity_ids_created = set([x['entity_id'] for x in history_data
                                  if x['event_type'] == history.EventTypes.create.value])
        entity_ids_modified = set([x['entity_id'] for x in history_data
                                  if x['event_type'] == history.EventTypes.modify.value])
        entity_ids_deleted = set([x['entity_id'] for x in history_data
                                  if x['event_type'] == history.EventTypes.delete.value])

        entity_ids_created_modified = list((entity_ids_created | entity_ids_modified) - entity_ids_deleted)

        entities_info_modified = entity_type_to_get_info_function[entity_type](
            entity_ids_created_modified
        )
        if entities_info_modified is None:
            entities_info_modified = []

        res = {'modified': entities_info_modified, 'deleted': list(entity_ids_deleted),
               'last_event_date': last_event_date}

    return res






