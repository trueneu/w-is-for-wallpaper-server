"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved

Business logic module + stupid arg checks/checking if GET returns None
"""

import logging
import datetime
import os
from itertools import chain
from w_is_for_wallpaper import mysqlpools as pools
from w_is_for_wallpaper import mysqlpool
from w_is_for_wallpaper import devices
from w_is_for_wallpaper import responder_helper
from w_is_for_wallpaper import mysql_db_themes_images
from w_is_for_wallpaper import entities
from w_is_for_wallpaper import dailies_rotator

POST_IMAGE_REQ_PARAMS = ['colors_matched', 'license', 'source', 'thumbnail',
                         'resolution', 'categories', 'origin']

PROTECTED_IMAGE_PARAMS = ['rating_multiplier', 'rating_addition', 'rating']
PROTECTED_IMAGE_MODIFY_PARAMS = ['votes']

RESOLUTION_REQ_FIELDS = ['width', 'height']

POST_CAT_REQ_PARAMS = ['name']

POST_COLOR_REQ_PARAMS = ['name', 'r', 'g', 'b']
POST_LICENSE_REQ_PARAMS = ['name', 'url']

POST_DAILY_REQ_PARAMS = ['image_id']

PROTECTED_CAT_PARAMS = ['image_id_daily_album_main_idx', 'image_id_daily_album_sec_idx',
                        'image_id_daily_portrait_main_idx', 'image_id_daily_portrait_sec_idx']


class ResponderException(Exception):
    pass


class NotFoundException(Exception):
    pass


def int_check(param):
    if param:
        try:
            int(param)
        except ValueError:
            raise ResponderException('id fields must be int.')


def daily_image_check(img_type, img_orientation):
    if ((img_type not in mysql_db_themes_images.DAILY_IMAGE_TYPE_TO_COLUMN) or
            (img_orientation not in mysql_db_themes_images.DAILY_IMAGE_ORIENTATION_TO_COLUMN)):
        raise ResponderException('Unknown type or orientation')


def expect_mysql_exception(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (mysqlpool.MysqlExecuteException, mysqlpool.MysqlPoolException) as e:
            str_e = str(e)
            logging.error(str_e)  # log actual error

            # if 'Duplicate entry' in str_e:
            #     error_description = 'MySQL: Duplicate entry on unique key. Please check the logs.'
            # else:
            #     error_description = 'MySQL: Please check the logs.'
            error_description = str_e
            msg = 'Error while responding to API call: %s' % error_description
            raise ResponderException(msg)  # hide the details from user
    return wrapped


# ############# COORD FUNCTIONS #############

@expect_mysql_exception
def get_coords_by_id(image_id):
    return responder_helper.get_all_coords_by_id(image_id)


# ############# IMAGE FUNCTIONS #############

# GET

@expect_mysql_exception
def get_images(image_id=None):
    int_check(image_id)
    res = responder_helper.get_images(image_id)
    if image_id and not res:
        raise NotFoundException('No image with such id: {id}'.format(id=image_id))
    return res


@expect_mysql_exception
def get_images_full_info_by_category_id(category_id):
    return responder_helper.get_images_full_info_by_category_id(category_id)


@expect_mysql_exception
def get_random_image(orientation, category_id, color_id):
    daily_image_check('main', orientation)
    int_check(color_id)
    image_info = responder_helper.get_random_image(orientation, category_id, color_id)

    if image_info is None:
        raise NotFoundException('No image could be found')
    return image_info


@expect_mysql_exception
def get_newest_images_count_by_category(category_ids_str, since_date_str):
    try:
        since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except (ValueError, TypeError):
        try:
            since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            raise ResponderException('Invalid since parameter supplied')

    if category_ids_str:
        try:
            category_ids = [int(x) for x in category_ids_str.split(',')]
        except (ValueError, TypeError, AttributeError):
            raise ResponderException('Invalid categories ids passed')
    else:
        category_ids = None

    return responder_helper.get_newest_images_count_by_category(category_ids, since_date)

# @expect_mysql_exception
# def get_images_full_info_newest(amount):
#     return responder_helper.get_images_full_info_newest(amount)

# POST


@expect_mysql_exception
def post_image(image_data):
    # stupid arg check
    try:
        if (not all([x in image_data for x in POST_IMAGE_REQ_PARAMS]) or
                not all([x in image_data['resolution'] for x in RESOLUTION_REQ_FIELDS])):
            raise ResponderException('Not enough fields to process the request')
    except (KeyError, TypeError):
        raise ResponderException('Not enough fields to process the request')
    if any([x in image_data for x in PROTECTED_IMAGE_PARAMS]):
        raise ResponderException('Trying to set one of protected params')
    res = responder_helper.post_image(image_data)
    if res is None:
        raise NotFoundException('One of categories or colors not found')
    return res


@expect_mysql_exception
def modify_image(image_id, image_data):
    int_check(image_id)
    if not image_id:
        raise ResponderException('You must supply data to change')
    if any([x in image_data for x in chain(PROTECTED_IMAGE_PARAMS, PROTECTED_IMAGE_MODIFY_PARAMS)]):
        raise ResponderException('Trying to set one of protected params')
    res = responder_helper.modify_image(image_id, image_data)
    if res is None:
        raise NotFoundException('Image, category or color not found')


@expect_mysql_exception
def delete_images(image_ids):
    res = responder_helper.delete_images(image_ids)
    if res is None:
        raise NotFoundException('One of images not found')


@expect_mysql_exception
def image_vote(image_id, votes_amount):
    res = responder_helper.image_vote(image_id, votes_amount)
    return res


@expect_mysql_exception
def recalculate_image_top():
    res = responder_helper.recalculate_image_top()
    return res


@expect_mysql_exception
def get_image_top(amount):
    res = responder_helper.get_image_top(amount)
    return res

# ############# CATEGORY FUNCTIONS #############


@expect_mysql_exception
def get_categories(cat_id=None):
    int_check(cat_id)
    res = responder_helper.get_categories(cat_id)
    if not res and cat_id:
        raise NotFoundException('No category with such id: {ids}'.format(ids=cat_id))
    return res


@expect_mysql_exception
def post_category(category_data):
    try:
        if not all([x in category_data for x in POST_CAT_REQ_PARAMS]):
            raise ResponderException('Not enough fields to process the request')
    except (KeyError, TypeError):
        raise ResponderException('Not enough fields to process the request')
    if any([x in category_data for x in PROTECTED_CAT_PARAMS]):
        raise ResponderException('Trying to set one of protected params')
    return responder_helper.post_category(category_data)


@expect_mysql_exception
def delete_categories(category_ids):
    res = responder_helper.delete_categories(category_ids)
    if res is None:
        raise NotFoundException('One of categories not found')


@expect_mysql_exception
def modify_category(category_id, category_data):
    int_check(category_id)
    if not category_data:
        raise ResponderException('You must supply data to change')
    if any([x in category_data for x in PROTECTED_CAT_PARAMS]):
        raise ResponderException('Trying to set one of protected params')
    res = responder_helper.modify_category(category_id, category_data)
    if res is None:
        raise NotFoundException('Category not found')


@expect_mysql_exception
def get_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_before_date_str):
    daily_image_check(daily_image_type, daily_image_orientation)
    try:
        daily_image_before_date = datetime.datetime.strptime(daily_image_before_date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except (ValueError, TypeError):
        try:
            daily_image_before_date = datetime.datetime.strptime(daily_image_before_date_str, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            raise ResponderException('Invalid since parameter supplied')

    res = responder_helper.get_daily_image(category_id, daily_image_type,
                                           daily_image_orientation, daily_image_before_date)
    if res is None:
        raise NotFoundException('No daily image found')
    return res


@expect_mysql_exception
def delete_daily_image(category_id, daily_image_type, daily_image_orientation):
    daily_image_check(daily_image_type, daily_image_orientation)
    res = responder_helper.delete_daily_image(category_id, daily_image_type, daily_image_orientation)
    return res


@expect_mysql_exception
def modify_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_data):
    if not all([x in daily_image_data for x in POST_DAILY_REQ_PARAMS]):
        raise ResponderException('Not enough fields to process the request')
    daily_image_check(daily_image_type, daily_image_orientation)
    res = responder_helper.modify_daily_image(category_id, daily_image_type, daily_image_orientation,
                                              daily_image_data['image_id'])
    return res


def rotate_dailies(category_ids=None, orientations=None):
    queue_dir_full_path = os.path.join(os.path.dirname(__file__), dailies_rotator.QUEUE_DIR)
    logging.info('queue_dir_full_path: {}'.format(queue_dir_full_path))
    logging.info('cwd: {}'.format(os.getcwd()))
    logging.info('__file__: {}'.format(__file__))
    if orientations:
        if not all([orientation in mysql_db_themes_images.DAILY_IMAGE_ORIENTATION_TO_COLUMN
                    for orientation in orientations]):
            raise ResponderException('Unknown orientation')
    try:
        os.mkdir(queue_dir_full_path)
    except FileExistsError:
        pass
    except OSError:
        raise ResponderException("Couldn't makedir for queues storage")
    return dailies_rotator.rotate_dailies(queue_dir_full_path, category_ids, orientations)

# ############# COLOR FUNCTIONS #############


@expect_mysql_exception
def get_colors(color_id=None):
    int_check(color_id)
    res = responder_helper.get_colors(color_id)
    if not res and color_id:
        raise NotFoundException('No colors with such color_id: {ids}'.format(ids=color_id))
    return res


@expect_mysql_exception
def post_color(color_data):
    try:
        if not(all([x in color_data for x in POST_COLOR_REQ_PARAMS])):
            raise ResponderException('Not enough fields to process the request')
    except (KeyError, TypeError):
        raise ResponderException('Not enough fields to process the request')
    return responder_helper.post_color(color_data)


@expect_mysql_exception
def modify_color(color_id, color_data):
    int_check(color_id)
    if not color_id:
        raise ResponderException('You must supply data to change')
    res = responder_helper.modify_color(color_id, color_data)
    if res is None:
        raise NotFoundException('Color not found')


@expect_mysql_exception
def delete_colors(color_ids):
    res = responder_helper.delete_colors(color_ids)
    if res is None:
        raise NotFoundException('One of colors not found')


# ############# LICENSE FUNCTIONS #############


@expect_mysql_exception
def get_licenses(license_id=None):
    int_check(license_id)
    res = responder_helper.get_licenses(license_id)
    if not res and license_id:
        raise NotFoundException('No license with such ids: {ids}'.format(ids=license_id))
    return res


@expect_mysql_exception
def post_license(license_data):
    try:
        if not(all([x in license_data for x in POST_LICENSE_REQ_PARAMS])):
            raise ResponderException('Not enough fields to process the request')
    except (KeyError, TypeError):
        raise ResponderException('Not enough fields to process the request')
    return responder_helper.post_license(license_data)


@expect_mysql_exception
def modify_license(license_id, license_data):
    int_check(license_id)
    if not license_id:
        raise ResponderException('You must supply data to change')
    res = responder_helper.modify_license(license_id, license_data)
    if res is None:
        raise NotFoundException('License not found')


@expect_mysql_exception
def delete_licenses(license_ids):
    res = responder_helper.delete_licenses(license_ids)
    if res is None:
        raise NotFoundException('One of licenses not found')

# ############# THEME FUNCTIONS #############


@expect_mysql_exception
def get_theme_full_info_by_id(theme_id):
    theme_info = pools.db_themes_images.get_theme_info_by_id(theme_id)
    image_info_desktop = (responder_helper.get_image_info_with_coords_by_id_device_type(
        theme_info['image_id_desktop'],
        devices.DeviceType.desktop)
                          if theme_info['image_id_desktop'] else
                          None)
    image_info_cellphone = (responder_helper.get_image_info_with_coords_by_id_device_type(
        theme_info['image_id_cellphone'],
        devices.DeviceType.cellphone)
                            if theme_info['image_id_cellphone'] else
                            None)
    image_info_band = (responder_helper.get_image_info_with_coords_by_id_device_type(
        theme_info['image_id_band'],
        devices.DeviceType.band)
                       if theme_info['image_id_band'] else
                       None)
    theme_info['images'] = {'desktop': image_info_desktop,
                            'cellphone': image_info_cellphone,
                            'band': image_info_band}
    return theme_info


@expect_mysql_exception
def get_themes_full_info():
    return responder_helper.get_themes_full_info()

# TODO pagination

# ############# HISTORY FUNCTIONS #############


@expect_mysql_exception
def get_history(since_date_str, entity_type):
    try:
        since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%dT%H:%M:%S.%f")
    except (ValueError, TypeError):
        try:
            since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            raise ResponderException('Invalid since parameter supplied')
    return responder_helper.get_history(since_date, entity_type)
