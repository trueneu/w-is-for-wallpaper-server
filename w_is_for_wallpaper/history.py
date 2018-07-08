from enum import Enum
from w_is_for_wallpaper import entities


class EventTypes(Enum):
    create = 1
    delete = 2
    modify = 3


table_entity_mapping = {
    'categories': entities.EntityTypes['category'],
    'colors': entities.EntityTypes['color'],
    'licenses': entities.EntityTypes['license'],
    'images': entities.EntityTypes['image'],
    'themes': entities.EntityTypes['theme'],
    'top': entities.EntityTypes['top'],
    'categories_to_images_mapping': entities.EntityTypes['image'],
    'colors_to_images_mapping': entities.EntityTypes['image'],
    'images_daily': entities.EntityTypes['image_daily']
}
