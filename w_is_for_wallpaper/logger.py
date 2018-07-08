"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

import logging
from w_is_for_wallpaper import config


loglevel_string = config.CONFIG["main"].get("loglevel")
try:
    loglevel = {"debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL}[loglevel_string]
except KeyError:
    loglevel = logging.ERROR

logfile = config.CONFIG["main"].get("logfile", "/var/log/wifw.log")
logging.basicConfig(level=loglevel,
                    format='[%(asctime)s] %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(logfile, 'a', 'utf-8')])
logging.debug("wfiw logger initialized")
