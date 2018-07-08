"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

import logging
from w_is_for_wallpaper import config
from w_is_for_wallpaper import mysqlpools as pools

config.read('wifw.conf')
from w_is_for_wallpaper import logger

logging.debug('wifw initialized')
pools.recreate_pools()

