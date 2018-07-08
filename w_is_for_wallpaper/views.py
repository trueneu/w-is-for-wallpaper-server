"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved

API endpoints defined here
"""

import flask
import json
import logging
import datetime
from functools import wraps
from w_is_for_wallpaper import app
from w_is_for_wallpaper import responder
from w_is_for_wallpaper import response_mime_retcode_helper
from w_is_for_wallpaper import entities
from w_is_for_wallpaper import dailies_rotator


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def expect_responder_exception(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            data = json.dumps(function(*args, **kwargs), separators=(',', ':'), default=json_serial)
            return response_mime_retcode_helper.json_200(data)
        except responder.ResponderException as e:
            return response_mime_retcode_helper.json_500(json.dumps({'status': 'ERROR', 'data': str(e)},
                                                                    separators=(',', ':')))
        except responder.NotFoundException as e:
            return response_mime_retcode_helper.json_404(json.dumps({'status': 'ERROR', 'data': str(e)},
                                                                    separators=(',', ':')))
    return wrapper


@app.errorhandler(500)
def internal_server_error(e):
    return response_mime_retcode_helper.json_500(json.dumps({'status': 'ERROR', 'data': str(e)},
                                                            separators=(',', ':')))


@app.errorhandler(404)
def not_found(e):
    return response_mime_retcode_helper.json_404(json.dumps({'status': 'ERROR', 'data': str(e)},
                                                            separators=(',', ':')))


# IMAGE ENDPOINTS

@app.route('/api/v1/images', methods=['GET', 'POST'])
@expect_responder_exception
def images():
    if flask.request.method == 'GET':
        return responder.get_images()
    elif flask.request.method == 'POST':
        return responder.post_image(flask.request.json)


@app.route('/api/v1/images/<image_id>', methods=['GET', 'DELETE', 'PUT'])
@expect_responder_exception
def get_image_info_by_id(image_id):
    if flask.request.method == 'GET':
        return responder.get_images(image_id)
    elif flask.request.method == 'DELETE':
        return responder.delete_images(image_id)
    elif flask.request.method == 'PUT':
        return responder.modify_image(image_id, flask.request.json)


@app.route('/api/v1/images/random', methods=['GET'])
@expect_responder_exception
def get_random_image():
    category_id = flask.request.args.get('category', None)
    orientation = flask.request.args.get('orientation', 'album')
    color_id = flask.request.args.get('color', None)
    if flask.request.method == 'GET':
        return responder.get_random_image(orientation, category_id, color_id)


# @app.route('/api/v1/images/newest')
# @expect_responder_exception
# def get_images_info_newest():
#     try:
#         amount = flask.request.args.get('amount', 5)  # TODO test passing a parameter, int and str
#     except KeyError:
#         amount = 5
#     return responder.get_images_full_info_newest(amount)

@app.route('/api/v1/images/count_newest_by_cat')
@expect_responder_exception
def get_newest_images_count_by_category():
    since_date = flask.request.args.get('since', None)
    category_ids = flask.request.args.get('categories')

    return responder.get_newest_images_count_by_category(category_ids, since_date)


@app.route('/api/v1/images/category/<category_id>')
@expect_responder_exception
def get_images_info_by_category_id(category_id):
    return responder.get_images_full_info_by_category_id(category_id)


@app.route('/api/v1/images/<image_id>/coords')
@expect_responder_exception
def get_coords_by_id(image_id):
    return responder.get_coords_by_id(image_id)


@app.route('/api/v1/images/<image_id>/vote_up', methods=['PUT'])
@expect_responder_exception
def image_vote_up(image_id):
    return responder.image_vote(image_id, 1)


@app.route('/api/v1/images/<image_id>/vote_down', methods=['PUT'])
@expect_responder_exception
def image_vote_down(image_id):
    return responder.image_vote(image_id, -1)


@app.route('/api/v1/images/history')
@expect_responder_exception
def image_history():
    since_date = flask.request.args.get('since', '2016-01-01T00:00:00')
    return responder.get_history(since_date, entities.EntityTypes.image)


@app.route('/api/v1/images/top', methods=['PUT', 'GET'])
@expect_responder_exception
def image_top():
    if flask.request.method == 'GET':
        amount = flask.request.args.get('amount', 50)
        return responder.get_image_top(amount)
    elif flask.request.method == 'PUT':
        return responder.recalculate_image_top()


# DAILY IMAGES ENDPOINTS
@app.route('/api/v1/categories/rotate_dailies', methods=['PUT', 'POST'])
@expect_responder_exception
def rotate_dailies():
    return responder.rotate_dailies()


@app.route('/api/v1/categories/<category_id>/daily', methods=['GET', 'DELETE', 'PUT', 'POST'])
@expect_responder_exception
def daily_images(category_id):
    daily_image_type = flask.request.args.get('type', 'main')
    daily_image_orientation = flask.request.args.get('orientation', 'album')
    daily_image_before_date = flask.request.args.get('before', datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
    if flask.request.method == 'GET':
        return responder.get_daily_image(category_id, daily_image_type, daily_image_orientation, daily_image_before_date)
    elif flask.request.method == 'DELETE':
        return responder.delete_daily_image(category_id, daily_image_type, daily_image_orientation)
    elif flask.request.method == 'PUT' or flask.request.method == 'POST':
        return responder.modify_daily_image(category_id, daily_image_type, daily_image_orientation, flask.request.json)


@app.route('/api/v1/categories/<category_id>/daily/rotate', methods=['PUT', 'POST'])
@expect_responder_exception
def rotate_daily(category_id):
    daily_image_orientation = flask.request.args.get('orientation', 'album')
    if flask.request.method == 'PUT' or flask.request.method == 'POST':
        return responder.rotate_dailies([category_id], [daily_image_orientation])


# CATEGORY ENDPOINTS


@app.route('/api/v1/categories', methods=['GET', 'POST'])
@expect_responder_exception
def categories():
    if flask.request.method == 'GET':
        return responder.get_categories()
    elif flask.request.method == 'POST':
        return responder.post_category(flask.request.json)


@app.route('/api/v1/categories/history')
@expect_responder_exception
def category_history():
    since_date = flask.request.args.get('since', '2016-01-01T00:00:00')
    return responder.get_history(since_date, entities.EntityTypes.category)


@app.route('/api/v1/categories/<category_id>', methods=['GET', 'DELETE', 'PUT'])
@expect_responder_exception
def category(category_id):
    if flask.request.method == 'GET':
        return responder.get_categories(category_id)
    elif flask.request.method == 'DELETE':
        return responder.delete_categories(category_id)
    elif flask.request.method == 'PUT':
        return responder.modify_category(category_id, flask.request.json)


# COLOR ENDPOINTS

@app.route('/api/v1/colors', methods=['GET', 'POST'])
@expect_responder_exception
def colors():
    if flask.request.method == 'GET':
        return responder.get_colors()
    elif flask.request.method == 'POST':
        return responder.post_color(flask.request.json)


@app.route('/api/v1/colors/<color_id>', methods=['GET', 'DELETE', 'PUT'])
@expect_responder_exception
def color(color_id):
    if flask.request.method == 'GET':
        return responder.get_colors(color_id)
    elif flask.request.method == 'DELETE':
        return responder.delete_colors(color_id)
    elif flask.request.method == 'PUT':
        return responder.modify_color(color_id, flask.request.json)


@app.route('/api/v1/colors/history')
@expect_responder_exception
def color_history():
    since_date = flask.request.args.get('since', '2016-01-01T00:00:00')
    return responder.get_history(since_date, entities.EntityTypes.color)

# LICENSE ENDPOINTS


@app.route('/api/v1/licenses', methods=['GET', 'POST'])
@expect_responder_exception
def licenses():
    if flask.request.method == 'GET':
        return responder.get_licenses()
    elif flask.request.method == 'POST':
        return responder.post_license(flask.request.json)


@app.route('/api/v1/licenses/<license_id>', methods=['GET', 'DELETE', 'PUT'])
@expect_responder_exception
def license_(license_id):
    if flask.request.method == 'GET':
        return responder.get_licenses(license_id)
    elif flask.request.method == 'DELETE':
        return responder.delete_licenses(license_id)
    elif flask.request.method == 'PUT':
        return responder.modify_license(license_id, flask.request.json)


@app.route('/api/v1/licenses/history')
@expect_responder_exception
def license_history():
    since_date = flask.request.args.get('since', '2016-01-01T00:00:00')
    return responder.get_history(since_date, entities.EntityTypes.license)


# THEME ENDPOINTS

@app.route('/api/v1/themes/<theme_id>')
@expect_responder_exception
def get_theme_info_by_id(theme_id):
    return responder.get_theme_full_info_by_id(theme_id)


@app.route('/api/v1/themes')
@expect_responder_exception
def get_themes_info():
    return responder.get_themes_full_info()


# HISTORY ENDPOINTS
@app.route('/api/v1/history')
@expect_responder_exception
def get_history():
    since_date = flask.request.args.get('since', '2016-01-01T00:00:00')
    return responder.get_history(since_date, entities.EntityTypes.everything)




