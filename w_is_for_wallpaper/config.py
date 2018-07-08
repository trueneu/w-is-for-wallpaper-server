"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

import configparser
import os


CONFIG = {}


class ConfigException(Exception):
    pass


def read(name='wifw.conf'):
    global CONFIG

    if not os.path.exists(name):
        raise ConfigException('Config {0} not found'.format(name))
    cp = configparser.ConfigParser()
    cp.read(name)

    res = {}
    for section in cp.sections():
        res[section] = {}
        for item, value in cp.items(section):
            if section.startswith('db') and (item == 'port' or item == 'pool_size'):
                res[section][item] = int(value)
            else:
                res[section][item] = value

    CONFIG = res
