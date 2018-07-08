"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

import logging

from w_is_for_wallpaper import initialize

logging.debug('wifw starting')

from flask import Flask

app = Flask(__name__)
from w_is_for_wallpaper import views


def main():
    app.run(host='127.0.0.1', port=8000)
    logging.debug("wifw died")


if __name__ == "__main__":
    main()
