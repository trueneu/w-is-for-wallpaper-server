"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""
from datetime import datetime
from enum import Enum
from w_is_for_wallpaper import mysqlpool
from w_is_for_wallpaper import devices
from w_is_for_wallpaper import entities
from w_is_for_wallpaper import history


class ParamType(Enum):
    none = 1,
    empty_lst = 2,
    lst = 3,
    value = 4


def get_param_type(param):
    if param is None:
        return ParamType.none
    if isinstance(param, list):
        if param:
            return ParamType.lst
        else:
            return ParamType.empty_lst
    return ParamType.value


IMG_COLUMNS = ['width', 'height', 'thumbnail',
               'source', 'id', 'license', 'uid', 'mtime', 'origin', 'votes']
COORDS_COLUMNS = ['x0', 'x1', 'width', 'height']
CATEGORY_ID_COLUMN = ['category_id']
CATEGORY_MAPPING_COLUMNS = ['category_id', 'image_id']
COLOR_MAPPING_COLUMNS = ['color_id', 'image_id']
COLORS_COLUMNS = ['id', 'name', 'r', 'g', 'b']
LICENSE_COLUMNS = ['id', 'name', 'url']
CATEGORY_COLUMNS = ['id', 'name', 'image_id_cover']
HISTORY_COLUMNS = ['id', 'event_type', 'entity_type', 'entity_id', 'date']

MAX_IMAGE_TOP_SIZE = 50

DAILY_IMAGE_TYPE_TO_COLUMN = {'main': 'main',
                              'sec': 'sec'}
DAILY_IMAGE_ORIENTATION_TO_COLUMN = {'album': 'album',
                                     'any': 'any'}

DAILY_IMAGE_TYPE_INT = {'main': {'any': 0, 'album': 1},
                        'sec': {'any': 2, 'album': 3}}


class DBThemesImages(mysqlpool.MysqlPool):
    """
    This class contains only methods used by responder on certain queries
    """

    # IMAGE METHODS

    def _generic_get_image_coords_by_id(self, image_id, table):
        return self.generic_select(table, ['x0', 'y0', 'width', 'height'],
                                   where={'image_id': {'values': image_id}})

    def get_image_coords_by_id_device_type(self, image_id, device_type):
        if device_type == devices.DeviceType.desktop:
            return self._generic_get_image_coords_by_id(image_id, 'image_coords_desktop')
        elif device_type == devices.DeviceType.cellphone:
            return self._generic_get_image_coords_by_id(image_id, 'image_coords_cellphone')
        elif device_type == devices.DeviceType.band:
            return self._generic_get_image_coords_by_id(image_id, 'image_coords_band')
        else:
            raise mysqlpool.MysqlExecuteException("Unknown device type: %s" % str(device_type))

    def get_image_categories_by_id(self, image_id):
        return self.generic_select('categories_to_images_mapping', ['category_id'],
                                   where={'image_id': {'values': image_id}},
                                   multiple_rows=True)

    def get_image_ids_by_category(self, category_id):
        return self.generic_select('categories_to_images_mapping', ['image_id'],
                                   where={'category_id': {'values': category_id}},
                                   multiple_rows=True)

    def get_image_ids_by_color(self, color_id):
        return self.generic_select('colors_to_images_mapping', ['image_id'],
                                   where={'color_id': {'values': color_id}},
                                   multiple_rows=True)

    def get_random_image_id(self, orientation, category_id, color_id):
        where = {}
        if orientation == 'album':
            where['width'] = {'values': '%height%', 'operator': '>'}

        id_values_set = set()
        if category_id:
            image_ids_in_category = [x['image_id'] for x in self.get_image_ids_by_category(category_id)]
            if not image_ids_in_category:
                return None
            id_values_set = set(image_ids_in_category)

        if color_id:
            image_ids_with_color = [x['image_id'] for x in self.get_image_ids_by_color(color_id)]
            if not image_ids_with_color:
                return None
            if id_values_set:
                id_values_set &= set(image_ids_with_color)
            else:
                id_values_set = set(image_ids_with_color)
        if id_values_set:
            where['id'] = {'values': list(id_values_set)}
        return self.generic_select('images', ['id'], where=where,
                                   order_by={'rand()': 'asc'}, multiple_rows=False, amount=1)

    def get_categories_images_are_daily_for(self, image_ids):
        res = list()
        for daily_image_type in DAILY_IMAGE_TYPE_TO_COLUMN:
            for daily_image_orientation in DAILY_IMAGE_ORIENTATION_TO_COLUMN:
                type_int = DBThemesImages.generate_daily_type_int(daily_image_type, daily_image_orientation)
                r = self.generic_select('images_daily', ['category_id'],
                                        where={'type': {'values': type_int}, 'image_id': {'values': image_ids}},
                                        multiple_rows=True)
                if r:
                    res.extend([{'category_id': x['category_id'], 'type': daily_image_type,
                                 'orientation': daily_image_orientation} for x in r])
        return res if res else None

    def delete_dailies_entries_by_images(self, image_ids):
        self.generic_delete('images_daily', where={'image_id': {'values': image_ids}})

    def delete_dailies_entries_by_categories(self, category_ids):
        self.generic_delete('images_daily', where={'category_id': {'values': category_ids}})

    def get_categories_images_are_cover_for(self, image_ids):
        r = self.generic_select('categories', ['id'], where={'image_id_cover': {'values': image_ids}}, multiple_rows=True)
        res = [{'category_id': x} for x in set([x['id'] for x in r])]
        return res if res else None

    def get_categories_mapping(self, image_ids, amount=1000):
        return self.generic_select('categories_to_images_mapping', CATEGORY_MAPPING_COLUMNS,
                                   where={'image_id': {'values': image_ids}},
                                   order_by={'image_id': 'asc'},
                                   multiple_rows=True, amount=amount)

    def get_colors_mapping(self, image_ids, amount=1000):
        return self.generic_select('colors_to_images_mapping', COLOR_MAPPING_COLUMNS,
                                   where={'image_id': {'values': image_ids}},
                                   order_by={'image_id': 'asc', 'ordering': 'asc'},
                                   multiple_rows=True, amount=amount)

    def get_images(self, ids, amount=1000):
        param_type = get_param_type(ids)
        if param_type == ParamType.none:
            images = self.generic_select('images', IMG_COLUMNS, multiple_rows=True, amount=amount)
        elif param_type == ParamType.lst:
            images = self.generic_select('images', IMG_COLUMNS, where={'id': {'values': ids}},
                                         multiple_rows=True, amount=amount)
        elif param_type == ParamType.value:
            images = self.generic_select('images', IMG_COLUMNS, where={'id': {'values': ids}},
                                         multiple_rows=False, amount=amount)
        elif param_type == ParamType.empty_lst:
            return None

        image_ids = [x['id'] for x in images]
        if not image_ids:
            return None
        categories_mapping = self.get_categories_mapping(image_ids, amount=amount)
        colors_mapping = self.get_colors_mapping(image_ids, amount=amount)

        # REWRITTEN VERSION
        categories_mapping_by_id = {}
        for mapping in categories_mapping:
            category_id, image_id = mapping['category_id'], mapping['image_id']
            try:
                categories_mapping_by_id[image_id].append(category_id)
            except KeyError:
                categories_mapping_by_id[image_id] = [category_id]
        for image in images:
            image_id = image['id']
            try:
                image['categories'] = sorted(categories_mapping_by_id[image_id])
            except KeyError:
                image['categories'] = []

        colors_mapping_by_id = {}
        for mapping in colors_mapping:
            color_id, image_id = mapping['color_id'], mapping['image_id']
            try:
                colors_mapping_by_id[image_id].append(color_id)
            except KeyError:
                colors_mapping_by_id[image_id] = [color_id]
        for image in images:
            image_id = image['id']
            try:
                image['colors_matched'] = colors_mapping_by_id[image_id]
            except KeyError:
                image['colors_matched'] = []

        return images

    def get_images_full_info_by_category(self, category_id):
        categories_mapping = self.generic_select('categories_to_images_mapping', CATEGORY_MAPPING_COLUMNS,
                                                 where={'category_id': {'values': category_id}},
                                                 order_by={'image_id': 'asc'},
                                                 multiple_rows=True)
        image_ids = [x['image_id'] for x in categories_mapping]
        return self.get_images(image_ids)

    def get_newest_images_count_by_category(self, category_ids, since_date):
        return self.generic_select('categories_to_images_mapping', ['count(distinct image_id)'],
                                   where={'category_id': {'values': category_ids},
                                          'mtime': {'values': since_date, 'operator': '>='}},
                                   multiple_rows=False)

    def get_newest_images_count(self, since_date):
        return self.generic_select('categories_to_images_mapping', ['count(distinct image_id)'],
                                   where={'mtime': {'values': since_date, 'operator': '>='}},
                                   multiple_rows=False)

    # def get_images_ids_newest(self, amount):
    #     return [x['id'] for x in self.generic_select('images', ['id'],
    #                                                  order_by={'mtime': 'desc'},
    #                                                  multiple_rows=True,
    #                                                  amount=amount)]

    # def get_images_full_info_newest(self, amount):
    #     image_ids_newest = self.get_images_ids_newest(amount)
    #     return self.get_images(image_ids_newest)

    def add_image(self, image_data):
        _, lastid = self.generic_insert('images', image_data, fetch_lastrowid=True)
        return lastid

    def modify_image(self, image_id, image_data):
        return self.update_by_id('images', image_data, image_id)

    def delete_images(self, image_ids):
        return self.delete_by_ids('images', image_ids)

    def recalculate_image_top(self, image_id):
        return self.update_by_id('images', {'rating': 'votes * rating_multiplier + rating_addition'}, image_id,
                                 write_history=False, smart_substitution=False)

    def modify_image_votes(self, image_id, diff):
        res = self.update_by_id('images', {'votes': 'votes + {diff}'.format(diff=diff)}, image_id,
                                write_history=False, smart_substitution=False)
        self.recalculate_image_top(image_id)
        return res

    # def add_image_top_coefficient(self, image_id, coeff_data):
    #     data = {'id': image_id}
    #     try:
    #         data.update(coeff_data)
    #     except TypeError:
    #         pass
    #     return self.generic_insert('image_top_coefficients', data, write_history=False)

    # def delete_images_top_coefficient(self, image_ids):
    #     self.delete_by_ids('image_top_coefficients', image_ids, write_history=False)

    def get_image_top(self, amount):
        return self.generic_select('images', ['id'], order_by={'rating': 'desc'}, multiple_rows=True, amount=amount)

    def recalculate_images_top(self):
        # TODO add multiplier/addition modify logic
        self._execute_queries(['UPDATE images SET rating = votes * rating_multiplier + rating_addition;'],
                              one_row=True)
        return [None]

    # CATEGORIES METHODS

    def add_category_image_mapping(self, categories_list, image_ids):
        if not categories_list:
            return None
        if not isinstance(image_ids, list):
            image_ids = [image_ids]
        res = self.generic_insert('categories_to_images_mapping',
                                  {'category_id': categories_list * len(image_ids),
                                   'image_id': [image_id for image_id in image_ids for _ in
                                                range(len(categories_list))],
                                   'mtime': [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')] * len(categories_list) * len(image_ids)},
                                  write_history=False)
        self.write_history(image_ids, history.EventTypes.modify, 'categories_to_images_mapping')
        return res

    def delete_category_image_mapping(self, categories_ids, image_ids):
        if not categories_ids:
            return None
        if not isinstance(image_ids, list):
            image_ids = [image_ids]
        res = self.generic_delete('categories_to_images_mapping', where={'category_id': {'values': categories_ids},
                                                                         'image_id': {'values': image_ids}})
        self.write_history(image_ids, history.EventTypes.modify, 'categories_to_images_mapping')
        return res

    def get_categories(self, cat_id=None):
        param_type = get_param_type(cat_id)
        if param_type == ParamType.none:
            return self.generic_select('categories', CATEGORY_COLUMNS, multiple_rows=True)
        elif param_type == ParamType.lst:
            return self.generic_select('categories', CATEGORY_COLUMNS, where={'id': {'values': cat_id}},
                                       multiple_rows=True)
        elif param_type == ParamType.value:
            return self.generic_select('categories', CATEGORY_COLUMNS, where={'id': {'values': cat_id}},
                                       multiple_rows=False)
        elif param_type == ParamType.empty_lst:
            return None

    def add_category(self, category_data):
        _, lastid = self.generic_insert('categories', category_data, fetch_lastrowid=True)
        return lastid

    def delete_categories(self, category_ids):
        return self.delete_by_ids('categories', category_ids)

    def modify_category(self, category_id, category_data):
        return self.update_by_id('categories', category_data, category_id)

    @staticmethod
    def generate_daily_column_name(daily_image_type, daily_image_orientation):
        return 'image_id_{img_ort}_{img_type}'.format(
            img_ort=DAILY_IMAGE_ORIENTATION_TO_COLUMN[daily_image_orientation],
            img_type=DAILY_IMAGE_TYPE_TO_COLUMN[daily_image_type])

    @staticmethod
    def generate_daily_type_int(daily_image_type, daily_image_orientation):
        return DAILY_IMAGE_TYPE_INT[daily_image_type][daily_image_orientation]

    def get_daily_image_id(self, category_id, daily_image_type, daily_image_orientation, daily_image_before_date):
        type_int = DBThemesImages.generate_daily_type_int(daily_image_type, daily_image_orientation)
        r = self.generic_select('images_daily', ['image_id'], where={'category_id': {'values': category_id},
                                                                     'type': {'values': type_int},
                                                                     'mtime': {'values': daily_image_before_date,
                                                                               'operator': '<='}},
                                order_by={'mtime': 'desc'}, amount=1,
                                multiple_rows=False)
        return r['image_id'] if r else None

    def delete_daily_image(self, category_id, daily_image_type, daily_image_orientation):
        now = datetime.utcnow()
        type_int = DBThemesImages.generate_daily_type_int(daily_image_type, daily_image_orientation)
        return self.generic_delete('images_daily', where={'category_id': {'values': category_id},
                                                          'type': {'values': type_int},
                                                          'mtime': {'values': now,
                                                                    'operator': '<='}},
                                   order_by={'mtime': 'desc'}, amount=1)

    def modify_daily_image(self, category_id, daily_image_type, daily_image_orientation, image_id):
        now = datetime.utcnow()
        type_int = DBThemesImages.generate_daily_type_int(daily_image_type, daily_image_orientation)
        return self.generic_insert('images_daily', {'category_id': category_id,
                                                    'type': type_int,
                                                    'image_id': image_id,
                                                    'mtime': now}, fetch_lastrowid=True, write_history=False)

    # COLOR METHODS

    def add_color_image_mapping(self, colors_list, image_ids):
        if not colors_list:
            return None
        if not isinstance(image_ids, list):
            image_ids = [image_ids]
        res = self.generic_insert('colors_to_images_mapping',
                                  {'color_id': colors_list,
                                   'image_id': [image_id for image_id in image_ids for _ in range(len(colors_list))],
                                   'mtime': [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')] * len(colors_list) * len(image_ids),
                                   'ordering': list(range(0, len(colors_list))) * len(image_ids)},
                                  write_history=False)
        self.write_history(image_ids, history.EventTypes.modify, 'colors_to_images_mapping')
        return res

    def delete_color_image_mapping(self, color_ids, image_ids):
        if not color_ids:
            return None
        if not isinstance(image_ids, list):
            image_ids = [image_ids]
        res = self.generic_delete('colors_to_images_mapping', where={'color_id': {'values': color_ids},
                                                                     'image_id': {'values': image_ids}})
        self.write_history(image_ids, history.EventTypes.modify, 'colors_to_images_mapping')
        return res

    def get_colors(self, color_id=None):
        param_type = get_param_type(color_id)
        if param_type == ParamType.none:
            return self.generic_select('colors', COLORS_COLUMNS, multiple_rows=True)
        elif param_type == ParamType.lst:
            return self.generic_select('colors', COLORS_COLUMNS, where={'id': {'values': color_id}},
                                       multiple_rows=True)
        elif param_type == ParamType.value:
            return self.generic_select('colors', COLORS_COLUMNS, where={'id': {'values': color_id}},
                                       multiple_rows=False)
        elif param_type.empty_lst:
            return None

    def add_color(self, color_data):
        _, lastid = self.generic_insert('colors', color_data, fetch_lastrowid=True)
        return lastid

    def delete_colors(self, color_ids):
        return self.delete_by_ids('colors', color_ids)

    def modify_color(self, color_id, color_data):
        return self.update_by_id('colors', color_data, color_id)

    # LICENSE METHODS

    def get_licenses(self, license_ids):
        param_type = get_param_type(license_ids)
        if param_type == ParamType.none:
            return self.generic_select('licenses', LICENSE_COLUMNS, multiple_rows=True)
        elif param_type == ParamType.lst:
            return self.generic_select('licenses', LICENSE_COLUMNS,
                                       where={'id': {'values': license_ids}},
                                       multiple_rows=True)
        elif param_type == ParamType.value:
            return self.generic_select('licenses', LICENSE_COLUMNS,
                                       where={'id': {'values': license_ids}},
                                       multiple_rows=False)
        elif param_type == ParamType.empty_lst:
            return None

    def add_license(self, license_data):
        _, lastid = self.generic_insert('licenses', license_data, fetch_lastrowid=True)
        return lastid

    def delete_licenses(self, license_ids):
        return self.delete_by_ids('licenses', license_ids)

    def modify_license(self, license_id, license_data):
        return self.update_by_id('licenses', license_data, license_id)

    # THEME METHODS

    def get_theme_info_by_id(self, theme_id):
        return self.generic_select('themes',
                                   ['name',
                                    'image_id_desktop',
                                    'image_id_cellphone',
                                    'image_id_band', 'id',
                                    'is_promoted'], {'id': theme_id})

    def get_themes_full_info(self):
        return self.generic_select_left_join(
            [('themes', 't'),
             ('images', 'imd'), ('image_coords_desktop', 'cd'),
             ('images', 'imc'), ('image_coords_cellphone', 'cc'),
             ('images', 'imb'), ('image_coords_band', 'cb')],
            [['id', 'name', 'is_promoted'],
             IMG_COLUMNS,
             COORDS_COLUMNS,
             IMG_COLUMNS,
             COORDS_COLUMNS,
             IMG_COLUMNS,
             COORDS_COLUMNS],
            [((1, 'id'), '=', (0, 'image_id_desktop')),
             ((2, 'image_id'), '=', (1, 'id')),
             ((3, 'id'), '=', (0, 'image_id_cellphone')),
             ((4, 'image_id'), '=', (3, 'id')),
             ((5, 'id'), '=', (0, 'image_id_band')),
             ((6, 'image_id'), '=', (5, 'id')),

             ])

    # HISTORY METHODS

    def get_history(self, since_date, entity_type=entities.EntityTypes.everything):
        if entity_type == entities.EntityTypes.everything:
            res = self.generic_select('history', HISTORY_COLUMNS,
                                      where={'date': {'values': since_date, 'operator': '>'}},
                                      order_by={'id': 'asc'},
                                      multiple_rows=True)
        else:
            res = self.generic_select('history', HISTORY_COLUMNS,
                                      where={'date': {'values': since_date, 'operator': '>'},
                                             'entity_type': {'values': entity_type.value}},
                                      order_by={'id': 'asc'},
                                      multiple_rows=True)

        return res
