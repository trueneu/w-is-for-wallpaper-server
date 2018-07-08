"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

from w_is_for_wallpaper import config

from w_is_for_wallpaper import mysql_db_categories
from w_is_for_wallpaper import mysql_db_themes_images
from w_is_for_wallpaper import mysql_db_ratings

import logging

db_themes_images = mysql_db_themes_images.DBThemesImages()  # duck typing hack
db_categories = mysql_db_categories.DBCategories()
db_ratings = mysql_db_ratings.DBRatings()

POOL_NAMES = ['db_themes_images']  # same as section names in config file

_pool_classes = {POOL_NAMES[0]: mysql_db_themes_images.DBThemesImages,
                 # POOL_NAMES[1]: mysql_db_categories.DBCategories,
                 # POOL_NAMES[2]: mysql_db_ratings.DBRatings
                 }


def recreate_pools():
    global db_themes_images, db_themes, db_categories, db_ratings
    logging.debug('initializing mysql pools...')
    db_themes_images = mysql_db_themes_images.DBThemesImages(
        pool_name='db_themes_images',
        **config.CONFIG['db_themes_images']
    )
    # db_categories = mysql_db_categories.DBCategories(pool_name='db_categories',
    #                                                  **config.CONFIG['db_categories'])
    # db_ratings = mysql_db_ratings.DBRatings(pool_name='db_ratings',
    #                                         **config.CONFIG['db_ratings'])

