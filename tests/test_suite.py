import requests
import json
import subprocess
import shlex
import sys
import os
import time
from datetime import datetime
import re
import shutil


def print_code_response(r):
    print("Code: %d" % r.status_code)
    print("Data: %s" % str(r.json()))
    print()


def delete_key(data, key):
    if isinstance(data, dict):
        del data[key]
    elif isinstance(data, list):
        for item in data:
            del item[key]


base_url = 'http://127.0.0.1:40443/api/v1'
categories_url = base_url + "/categories"
colors_url = base_url + "/colors"
licenses_url = base_url + "/licenses"
images_url = base_url + "/images"
history_url = base_url + "/history"

shutil.rmtree('../w_is_for_wallpaper/daily_queues', ignore_errors=True)

print("Dumping database structure...")
cmd = './make_a_dump_without_data.sh wifw'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))

print("Resetting autoincrements...")
cmd = './dump_reset_auto_increment.sh wifw.sql'
assert not (subprocess.check_call(shlex.split(cmd)))

print("Recreating the database...")
cmd = './restore_dump.sh wifw'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))

# 404 / 200 empty

print("Reading categories")
r = requests.get(categories_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == []

print("Reading category, id == 11")
r = requests.get(categories_url + '/11')
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'data': 'No category with such id: 11', 'status': 'ERROR'}

print("Reading colors")
r = requests.get(colors_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == []

print("Reading color, id == 3")
r = requests.get(colors_url + '/3')
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'status': 'ERROR', 'data': 'No colors with such color_id: 3'}

print("Reading all images")
r = requests.get(images_url)
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == []

print("Reading image, id == 5")
r = requests.get(images_url + "/5")
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'status': 'ERROR', 'data': 'No image with such id: 5'}

print("Reading licenses")
r = requests.get(licenses_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == []

print("Reading license, id == 1")
r = requests.get(licenses_url + "/1")
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'data': 'No license with such ids: 1', 'status': 'ERROR'}

# CATEGORIES
data = [{'name': 'DEFAULT'},
        {'name': 'Abstraction'},
        {'name': 'Windows'},
        {'name': 'Animals'},
        {'name': 'Aviation'},
        {'name': 'Cars'},
        {'name': 'City'},
        {'name': 'Army'},
        {'name': 'Space'},
        {'name': 'Tech'},
        {'name': 'Elements'},
        {'name': 'FoodAndDrink'},
        {'name': 'Dark'},
        {'name': 'Games'},
        {'name': 'Love'},
        {'name': 'Sport'},
        {'name': 'Water'},
        {'name': 'Sky'},
        {'name': 'Nature'},
        {'name': 'Music'},
        {'name': 'Movies'},
        {'name': 'Vintage'},
        {'name': 'Seasons'},
        {'name': 'Moto'},
        {'name': 'Minimalism'}]

for index, entry in enumerate(data):
    r = requests.post(categories_url, json=entry)
    print_code_response(r)
    assert r.status_code == 200
    assert r.json() == {'id': index + 1}

date_category_26_added = datetime.utcnow()
time.sleep(1)
data = {'name': 'Macro'}
r = requests.post(categories_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 26}

print("Reading categories")
r = requests.get(categories_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == [{'id': 1, 'name': 'DEFAULT'}, {'id': 2, 'name': 'Abstraction'}, {'id': 3, 'name': 'Windows'},
                    {'id': 4, 'name': 'Animals'}, {'id': 5, 'name': 'Aviation'}, {'id': 6, 'name': 'Cars'},
                    {'id': 7, 'name': 'City'}, {'id': 8, 'name': 'Army'}, {'id': 9, 'name': 'Space'},
                    {'id': 10, 'name': 'Tech'}, {'id': 11, 'name': 'Elements'}, {'id': 12, 'name': 'FoodAndDrink'},
                    {'id': 13, 'name': 'Dark'}, {'id': 14, 'name': 'Games'}, {'id': 15, 'name': 'Love'},
                    {'id': 16, 'name': 'Sport'}, {'id': 17, 'name': 'Water'}, {'id': 18, 'name': 'Sky'},
                    {'id': 19, 'name': 'Nature'}, {'id': 20, 'name': 'Music'}, {'id': 21, 'name': 'Movies'},
                    {'id': 22, 'name': 'Vintage'}, {'id': 23, 'name': 'Seasons'}, {'id': 24, 'name': 'Moto'},
                    {'id': 25, 'name': 'Minimalism'}, {'id': 26, 'name': 'Macro'}]

print("Reading category, id == 11")
r = requests.get(categories_url + '/11')
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 11, 'name': 'Elements'}

print("Reading category, id == 100")
r = requests.get(categories_url + '/100')
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'status': 'ERROR', 'data': 'No category with such id: 100'}

# COLORS
data = {"name": ["Black",
                 "Red",
                 "Green",
                 "Blue"],
        "r": [0, 1, 2, 3],
        "g": [0, 1, 2, 3],
        "b": [0, 1, 2, 3]}

print("Writing colors")
r = requests.post(colors_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 1}

print("Reading colors")
r = requests.get(colors_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == [{'id': 1, 'name': 'Black', 'r': 0, 'g': 0, 'b': 0},
                    {'id': 2, 'name': 'Red', 'r': 1, 'g': 1, 'b': 1},
                    {'id': 3, 'name': 'Green', 'r': 2, 'g': 2, 'b': 2},
                    {'id': 4, 'name': 'Blue', 'r': 3, 'g': 3, 'b': 3}]

print("Reading color, id == 3")
r = requests.get(colors_url + '/3')
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 3, 'name': 'Green', 'r': 2, 'g': 2, 'b': 2}

print("Reading color, id == 100")
r = requests.get(colors_url + '/100')
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'status': 'ERROR', 'data': 'No colors with such color_id: 100'}

# LICENSES

data = {'name': 'Creative Commons',
        'url': 'http://creative-commons.com/license'}

print("Writing licenses")
r = requests.post(licenses_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 1}

print("Reading licenses")
r = requests.get(licenses_url)
print_code_response(r)
assert r.status_code == 200
assert r.json() == [{'id': 1, 'name': 'Creative Commons', 'url': 'http://creative-commons.com/license'}]

data = {'name': 'Hueative Huyommons'}
print("Attempting to write a license without URL parameter")
r = requests.post(licenses_url, json=data)
print_code_response(r)
assert r.status_code == 500
assert r.json() == {'status': 'ERROR', 'data': "Not enough fields to process the request"}

print("Reading license, id == 1")
r = requests.get(licenses_url + "/1")
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 1, 'name': 'Creative Commons', 'url': 'http://creative-commons.com/license'}

# IMAGES
data = {
        'license': 1,
        'source': 'http://scarlett-johanson.com/boobs.jpg',
        'thumbnail': 'http://scarlett-johanson.com/thumbnail_boobs.jpg',
        'colors_matched': [2],
        'resolution': {'width': 200, 'height': 100},
        'categories': [1, 4],
        'origin': 'origin_test',
        'votes': 10
        }
print("Writing images")
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 1}

data = {
        'license': 1,
        'source': 'http://grass.com',
        'thumbnail': 'http://grass.com/thumb',
        'colors_matched': [2],
        'resolution': {'width': 200, 'height': 100},
        'categories': [1, 4],
        'origin': '',
        'votes': 20
        }
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 2}

data = {
        'license': 1,
        'source': 'http://grass3.com',
        'thumbnail': 'http://grass.com/thumb',
        'colors_matched': [2],
        'resolution': {'width': 50, 'height': 100},
        'categories': [2, 4],
        'origin': 'origin_test',
        'votes': 30
        }
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 3}

data = {
        'license': 1,
        'source': 'http://grass4.com',
        'thumbnail': 'http://grass.com/thumb',
        'colors_matched': [2],
        'resolution': {'width': 100, 'height': 100},
        'categories': [3, 4],
        'origin': 'origin_test',
        'votes': 40
        }
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 4}

dt = re.sub(r'\.\d+$', '', date_category_26_added.isoformat())
print('Checking count of new images in category 1')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="1"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 2}

print('Checking count of new images in category 2')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="2"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 1}

print('Checking count of new images in category 20')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="20"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 0}

time.sleep(2)
date_image_5_added = datetime.utcnow()
data = {
        'license': 1,
        'source': 'http://grass5.com',
        'thumbnail': 'http://grass.com/thumb',
        'colors_matched': [2],
        'resolution': {'width': 50, 'height': 100},
        'categories': [2, 3, 4],
        'origin': 'origin_test',
        'votes': 50

        }
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 5}

print('Checking count of new images in category 2')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="2"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 2}

print("Writing a duplicate image")
data = {
        'license': 1,
        'source': 'http://grass.com',
        'thumbnail': 'http://grass.com/thumb',
        'colors_matched': [1],
        'resolution': {'width': 100, 'height': 100},
        'categories': [7],
        'origin': 'origin_test',
        'votes': 50
        }
r = requests.post(images_url, json=data)
print_code_response(r)
assert r.status_code == 500
assert r.json() == {'status': 'ERROR',
                    'data': 'Error while responding to API call: MySQL: Duplicate entry on unique key. Please check the logs.'}

print("Reading image, id == 5")
r = requests.get(images_url + "/5")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass5.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [2],
                'resolution': {'width': 50, 'height': 100},
                'uid': '55f2e2be461f1f7d6c98653cf9ad2099',

                'categories': [2, 3, 4],
                'id': 5,
                'origin': 'origin_test',
                'votes': 50,

                }

print("Reading all images")
r = requests.get(images_url)
assert r.status_code == 200
print_code_response(r)
data = r.json()
delete_key(data, 'mtime')
assert data == [{'colors_matched': [2], 'license': 1,
                 'uid': '60168a14f921a2390714180308f91d6b', 'source': 'http://scarlett-johanson.com/boobs.jpg',
                  'votes': 10,
                 'thumbnail': 'http://scarlett-johanson.com/thumbnail_boobs.jpg', 'categories': [1, 4], 'id': 1,
                 'resolution': {'height': 100, 'width': 200}, 'origin': 'origin_test', },
                {'colors_matched': [2], 'license': 1,
                 'uid': 'ccc830035872ae9a97c069ed2a4c12a0', 'source': 'http://grass.com',
                 'votes': 20, 'thumbnail': 'http://grass.com/thumb', 'categories': [1, 4], 'id': 2,
                 'resolution': {'height': 100, 'width': 200}, 'origin': '', },
                {'colors_matched': [2], 'license': 1,
                 'uid': '07b72b842c867f3327a4b70be124d1be', 'source': 'http://grass3.com',
                 'votes': 30, 'thumbnail': 'http://grass.com/thumb', 'categories': [2, 4], 'id': 3,
                 'resolution': {'height': 100, 'width': 50}, 'origin': 'origin_test', },
                {'colors_matched': [2], 'license': 1,
                 'uid': '89ae384112b1afdf9bdaa9187a77750c', 'source': 'http://grass4.com',
                 'votes': 40, 'thumbnail': 'http://grass.com/thumb', 'categories': [3, 4], 'id': 4,
                 'resolution': {'height': 100, 'width': 100}, 'origin': 'origin_test', },
                {'colors_matched': [2], 'license': 1,
                 'uid': '55f2e2be461f1f7d6c98653cf9ad2099', 'source': 'http://grass5.com',
                 'votes': 50, 'thumbnail': 'http://grass.com/thumb', 'categories': [2, 3, 4], 'id': 5,
                 'resolution': {'height': 100, 'width': 50}, 'origin': 'origin_test', }]

print("Reading all history")
r = requests.get(history_url)
assert r.status_code == 200
print_code_response(r)
data = r.json()
delete_key(data, 'date')
for d in data:
    print('{' + "'id': {}, 'entity_id': {}, 'event_type': {}, 'entity_type': {}".format(
        d['id'], d['entity_id'], d['event_type'], d['entity_type']
    ) + '}')

assert data == [{'id': 1, 'entity_id': 1, 'event_type': 1, 'entity_type': 1},
                {'id': 2, 'entity_id': 2, 'event_type': 1, 'entity_type': 1},
                {'id': 3, 'entity_id': 3, 'event_type': 1, 'entity_type': 1},
                {'id': 4, 'entity_id': 4, 'event_type': 1, 'entity_type': 1},
                {'id': 5, 'entity_id': 5, 'event_type': 1, 'entity_type': 1},
                {'id': 6, 'entity_id': 6, 'event_type': 1, 'entity_type': 1},
                {'id': 7, 'entity_id': 7, 'event_type': 1, 'entity_type': 1},
                {'id': 8, 'entity_id': 8, 'event_type': 1, 'entity_type': 1},
                {'id': 9, 'entity_id': 9, 'event_type': 1, 'entity_type': 1},
                {'id': 10, 'entity_id': 10, 'event_type': 1, 'entity_type': 1},
                {'id': 11, 'entity_id': 11, 'event_type': 1, 'entity_type': 1},
                {'id': 12, 'entity_id': 12, 'event_type': 1, 'entity_type': 1},
                {'id': 13, 'entity_id': 13, 'event_type': 1, 'entity_type': 1},
                {'id': 14, 'entity_id': 14, 'event_type': 1, 'entity_type': 1},
                {'id': 15, 'entity_id': 15, 'event_type': 1, 'entity_type': 1},
                {'id': 16, 'entity_id': 16, 'event_type': 1, 'entity_type': 1},
                {'id': 17, 'entity_id': 17, 'event_type': 1, 'entity_type': 1},
                {'id': 18, 'entity_id': 18, 'event_type': 1, 'entity_type': 1},
                {'id': 19, 'entity_id': 19, 'event_type': 1, 'entity_type': 1},
                {'id': 20, 'entity_id': 20, 'event_type': 1, 'entity_type': 1},
                {'id': 21, 'entity_id': 21, 'event_type': 1, 'entity_type': 1},
                {'id': 22, 'entity_id': 22, 'event_type': 1, 'entity_type': 1},
                {'id': 23, 'entity_id': 23, 'event_type': 1, 'entity_type': 1},
                {'id': 24, 'entity_id': 24, 'event_type': 1, 'entity_type': 1},
                {'id': 25, 'entity_id': 25, 'event_type': 1, 'entity_type': 1},
                {'id': 26, 'entity_id': 26, 'event_type': 1, 'entity_type': 1},
                {'id': 27, 'entity_id': 1, 'event_type': 1, 'entity_type': 2},
                {'id': 28, 'entity_id': 2, 'event_type': 1, 'entity_type': 2},
                {'id': 29, 'entity_id': 3, 'event_type': 1, 'entity_type': 2},
                {'id': 30, 'entity_id': 4, 'event_type': 1, 'entity_type': 2},
                {'id': 31, 'entity_id': 1, 'event_type': 1, 'entity_type': 3},
                {'id': 32, 'entity_id': 1, 'event_type': 1, 'entity_type': 4},
                {'id': 33, 'entity_id': 1, 'event_type': 3, 'entity_type': 4},
                {'id': 34, 'entity_id': 1, 'event_type': 3, 'entity_type': 4},
                {'id': 35, 'entity_id': 2, 'event_type': 1, 'entity_type': 4},
                {'id': 36, 'entity_id': 2, 'event_type': 3, 'entity_type': 4},
                {'id': 37, 'entity_id': 2, 'event_type': 3, 'entity_type': 4},
                {'id': 38, 'entity_id': 3, 'event_type': 1, 'entity_type': 4},
                {'id': 39, 'entity_id': 3, 'event_type': 3, 'entity_type': 4},
                {'id': 40, 'entity_id': 3, 'event_type': 3, 'entity_type': 4},
                {'id': 41, 'entity_id': 4, 'event_type': 1, 'entity_type': 4},
                {'id': 42, 'entity_id': 4, 'event_type': 3, 'entity_type': 4},
                {'id': 43, 'entity_id': 4, 'event_type': 3, 'entity_type': 4},
                {'id': 44, 'entity_id': 5, 'event_type': 1, 'entity_type': 4},
                {'id': 45, 'entity_id': 5, 'event_type': 3, 'entity_type': 4},
                {'id': 46, 'entity_id': 5, 'event_type': 3, 'entity_type': 4}]


print("Reading history since last image was added")
dt = re.sub(r'\.\d+$', '', date_image_5_added.isoformat())
print(dt)
r = requests.get(history_url + '?since={dt}'.format(dt=dt))
print_code_response(r)
data = r.json()
delete_key(data, 'date')
assert r.status_code == 200
assert data == [{'id': 44, 'entity_id': 5, 'event_type': 1, 'entity_type': 4},
                {'id': 45, 'entity_id': 5, 'event_type': 3, 'entity_type': 4},
                {'id': 46, 'entity_id': 5, 'event_type': 3, 'entity_type': 4}]

time.sleep(1)

date_category_20_deleted = datetime.utcnow()

print("Deleting category 20")
r = requests.delete(categories_url + '/20')
print_code_response(r)
assert r.status_code == 200

print("Verify")
r = requests.get(categories_url + '/20')
print_code_response(r)
assert r.status_code == 404
assert r.json() == {'data': 'No category with such id: 20', 'status': 'ERROR'}

print("Deleting category 40 (non-existent)")
r = requests.delete(categories_url + '/40')
print_code_response(r)
assert r.status_code == 404

print("Reading category history since 20 was deleted")
dt = re.sub(r'\.\d+$', '', date_category_20_deleted.isoformat())
print(dt)
r = requests.get(categories_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'deleted': [20], 'modified': []}

print("Modifying category 10")
data = {'name': 'Hyuategoriya'}
r = requests.put(categories_url + '/10', json=data)
print_code_response(r)
assert r.status_code == 200

print("Reading category history since 20 was deleted")
dt = re.sub(r'\.\d+$', '', date_category_20_deleted.isoformat())
print(dt)
r = requests.get(categories_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 10, 'name': 'Hyuategoriya'}],
                    'deleted': [20]}

print("Modifying category 40 (non-existent)")
data = {'name': 'Hyuategoriya'}
r = requests.put(categories_url + '/40', json=data)
print_code_response(r)
assert r.status_code == 404

print("Modifying category 10 with no data")
data = {'name': 'Hyuategoriya'}
r = requests.put(categories_url + '/10')
print_code_response(r)
assert r.status_code == 500

print("Testing if history hasn't changed since checked the last time")
dt = re.sub(r'\.\d+$', '', date_category_20_deleted.isoformat())
print(dt)
r = requests.get(categories_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 10, 'name': 'Hyuategoriya'}],
                    'deleted': [20]}

date_license_2_added = datetime.utcnow()
dt = re.sub(r'\.\d+$', '', date_license_2_added.isoformat())

data = {'name': 'Creative Commons2',
        'url': 'http://creative-commons.com2/license'}

print("Writing license 2")
r = requests.post(licenses_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 2}

print("Reading license history")
r = requests.get(licenses_url + '/history')
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 1, 'name': 'Creative Commons', 'url': 'http://creative-commons.com/license'},
                                 {'id': 2, 'name': 'Creative Commons2', 'url': 'http://creative-commons.com2/license'}],
                    'deleted': []}

print("Reading license history since 2 was added")
r = requests.get(licenses_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 2, 'name': 'Creative Commons2', 'url': 'http://creative-commons.com2/license'}],
                    'deleted': []}

print("Modifying a license")
data = {'name': 'Creative Huyommons2'}
r = requests.put(licenses_url + '/2', json=data)
print_code_response(r)
assert r.status_code == 200

print("Reading license history since 2 was added")
r = requests.get(licenses_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {
    'modified': [{'id': 2, 'name': 'Creative Huyommons2', 'url': 'http://creative-commons.com2/license'}],
    'deleted': []}

print("Deleting a license")
r = requests.delete(licenses_url + '/2')
print_code_response(r)
assert r.status_code == 200

print("Reading license history since 2 was added")
r = requests.get(licenses_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [],
                    'deleted': [2]}

date_color_5_added = datetime.utcnow()
dt = re.sub(r'\.\d+$', '', date_color_5_added.isoformat())

data = {'name': 'Gray', 'r': 4, 'g': 4, 'b': 4}

print("Writing color 5")
r = requests.post(colors_url, json=data)
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'id': 5}

print("Reading color history")
r = requests.get(colors_url + '/history')
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 1, 'name': 'Black', 'r': 0, 'g': 0, 'b': 0},
                                 {'id': 2, 'name': 'Red', 'r': 1, 'g': 1, 'b': 1},
                                 {'id': 3, 'name': 'Green', 'r': 2, 'g': 2, 'b': 2},
                                 {'id': 4, 'name': 'Blue', 'r': 3, 'g': 3, 'b': 3},
                                 {'id': 5, 'name': 'Gray', 'r': 4, 'g': 4, 'b': 4}],
                    'deleted': []}

print("Reading color history since 5 was added")
r = requests.get(colors_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 5, 'name': 'Gray', 'r': 4, 'g': 4, 'b': 4}],
                    'deleted': []}

print("Modifying a color")
data = {'name': 'Grey'}
r = requests.put(colors_url + '/5', json=data)
print_code_response(r)
assert r.status_code == 200

print("Reading colors history since 5 was added")
r = requests.get(colors_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [{'id': 5, 'name': 'Grey', 'r': 4, 'g': 4, 'b': 4}],
                    'deleted': []}

print("Deleting a color")
r = requests.delete(colors_url + '/5')
print_code_response(r)
assert r.status_code == 200

print("Reading colors history since 5 was added")
r = requests.get(colors_url + '/history?since={dt}'.format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [],
                    'deleted': [5]}

print("Deleting a color that's linked to an image")
r = requests.delete(colors_url + '/2')
print_code_response(r)
assert r.status_code == 500

print("Deleting a license that's linked to an image")
r = requests.delete(licenses_url + '/1')
print_code_response(r)
assert r.status_code == 500

print("Deleting a category that's linked to an image")
r = requests.delete(categories_url + '/1')
print_code_response(r)
assert r.status_code == 500

date_image_5_modified = datetime.utcnow()
dt = re.sub(r'\.\d+$', '', date_image_5_modified.isoformat())

time.sleep(1)
# data = {'name': 'Grass 555',
#         'license': 1,
#         'source': 'http://grass5.com',
#         'thumbnail': 'http://grass.com/thumb',
#         'colors_matched': 2,
#         'average_color': {'r': 100, 'g': 200, 'b': 0},
#         'resolution': {'width': 50, 'height': 100},
#         'categories': [2, 3, 4]
#         }

data = {'name': 'Grass 555'}
print('Modifying image 5')
r = requests.put(images_url + '/5', json=data)
print_code_response(r)
assert r.status_code == 200

print('Checking modification results')
r = requests.get(images_url + "/5")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass5.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [2],
                'resolution': {'width': 50, 'height': 100},
                'uid': '55f2e2be461f1f7d6c98653cf9ad2099',

                'categories': [2, 3, 4],
                'id': 5,
                'origin': 'origin_test',
                'votes': 50,
                }

data = {'categories': [50]}
print('Trying to assign non-exsistent category')
r = requests.put(images_url + '/5', json=data)
print_code_response(r)
assert r.status_code == 404

data = {'categories': [5, 6]}
print('Changing categories')
r = requests.put(images_url + '/5', json=data)
print_code_response(r)
assert r.status_code == 200

print('Checking modification results')
r = requests.get(images_url + "/5")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass5.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [2],
                'resolution': {'width': 50, 'height': 100},
                'uid': '55f2e2be461f1f7d6c98653cf9ad2099',

                'categories': [5, 6],
                'id': 5,
                'origin': 'origin_test',
                'votes': 50,

                }

data = {'source': 'http://grass555.com'}
print('Changing source. uid must change')
r = requests.put(images_url + '/5', json=data)
print_code_response(r)
assert r.status_code == 200

print('Checking modification results')
r = requests.get(images_url + "/5")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass555.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [2],
                'resolution': {'width': 50, 'height': 100},
                'uid': '8f7dde0d0209a622ec64a5de94ab80b8',

                'categories': [5, 6],
                'id': 5,
                'origin': 'origin_test',
                'votes': 50,
                }

dt = re.sub(r'\.\d+$', '', date_category_26_added.isoformat())
print('Checking count of new images in category 6')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="6"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 1}

dt = re.sub(r'\.\d+$', '', date_image_5_modified.isoformat())
print('Checking count of new images in category 5 since image 5 was modified')
r = requests.get(images_url + '/count_newest_by_cat?since={dt}&categories={c}'.format(
    dt=dt, c="6"
))
print_code_response(r)
assert r.status_code == 200
assert r.json() == {'count': 1}

print('Checking history since 5 was modified')
r = requests.get(images_url + "/history?since={dt}".format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data['modified'], 'mtime')
delete_key(data, 'last_event_date')
assert data == {'modified': [{
                              'license': 1,
                              'source': 'http://grass555.com',
                              'thumbnail': 'http://grass.com/thumb',
                              'colors_matched': [2],
                              'resolution': {'width': 50, 'height': 100},
                              'uid': '8f7dde0d0209a622ec64a5de94ab80b8',

                              'categories': [5, 6],
                              'id': 5,
                              'origin': 'origin_test',
                              'votes': 50,
                              }
                             ],
                'deleted': []}

time.sleep(1)
date_image_5_deleted = datetime.utcnow()
dt = re.sub(r'\.\d+$', '', date_image_5_deleted.isoformat())

print("Deleting image 5")
r = requests.delete(images_url + "/5")
print_code_response(r)
assert r.status_code == 200

print('Checking history since 5 was deleted')
r = requests.get(images_url + "/history?since={dt}".format(dt=dt))
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'last_event_date')
assert data == {'modified': [], 'deleted': [5]}

print('Vote image 4 up')
r = requests.put(images_url + "/4/vote_up")
print_code_response(r)
assert r.status_code == 200

print('Vote image 4 down 2 times')
r = requests.put(images_url + "/4/vote_down")
print_code_response(r)
assert r.status_code == 200

r = requests.put(images_url + "/4/vote_down")
print_code_response(r)
assert r.status_code == 200

print('Check results')
r = requests.get(images_url + "/4")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass4.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [2],
                'resolution': {'width': 100, 'height': 100},
                'categories': [3, 4],
                'origin': 'origin_test',
                'votes': 39,
                'uid': '89ae384112b1afdf9bdaa9187a77750c',
                'id': 4,


                }

print('Remembering history')
r = requests.get(history_url)
his = r.json()

dailies = ['', '?orientation=any']

print('Checking that no dailies set for cat 1')
for d in dailies:
    r = requests.get(categories_url + '/1/daily' + d)
    print_code_response(r)
    assert r.status_code == 404

os.chdir(os.path.dirname(os.getcwd()))
print(os.getcwd())

print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies')
r = requests.get(categories_url + '/1/daily')
print_code_response(r)
assert r.json()['id'] == 1
r = requests.get(categories_url + '/1/daily?orientation=any')
assert r.json()['id'] == 1

r = requests.get(categories_url + '/2/daily')
assert r.status_code == 404
r = requests.get(categories_url + '/2/daily?orientation=any')
assert r.json()['id'] == 3

r = requests.get(categories_url + '/3/daily')
assert r.status_code == 404
r = requests.get(categories_url + '/3/daily?orientation=any')
assert r.json()['id'] == 4

r = requests.get(categories_url + '/4/daily')
assert r.json()['id'] == 1
r = requests.get(categories_url + '/4/daily?orientation=any')
assert r.json()['id'] == 1

print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies for cat 4')
r = requests.get(categories_url + '/4/daily')
assert r.json()['id'] == 2
r = requests.get(categories_url + '/4/daily?orientation=any')
assert r.json()['id'] == 2

print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies for cat 4')
r = requests.get(categories_url + '/4/daily')
assert r.json()['id'] == 1
r = requests.get(categories_url + '/4/daily?orientation=any')
assert r.json()['id'] == 3


print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies for cat 4')
r = requests.get(categories_url + '/4/daily')
assert r.json()['id'] == 2
r = requests.get(categories_url + '/4/daily?orientation=any')
assert r.json()['id'] == 4


print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies for cat 4')
r = requests.get(categories_url + '/4/daily')
assert r.json()['id'] == 1
r = requests.get(categories_url + '/4/daily?orientation=any')
assert r.json()['id'] == 1

print('Setting improper dailies for cat 1')
for i, d in enumerate(dailies):
    data = {'image_id': i + 3}
    print(data)
    r = requests.post(categories_url + '/1/daily' + d, json=data)
    print_code_response(r)
    assert r.status_code == 200

print('Checking that dailies again')
for i, d in enumerate(dailies):
    r = requests.get(categories_url + '/1/daily' + d)
    print_code_response(r)
    data = r.json()
    assert 'id' in data and data['id'] == i + 3

print('Rotating dailies')
cmd = 'python3 ./w_is_for_wallpaper/dailies_rotator.py'
assert not (subprocess.check_call(shlex.split(cmd), stderr=subprocess.DEVNULL))
print('Checking dailies for cat 1, should be proper')
r = requests.get(categories_url + '/1/daily')
assert r.json()['id'] == 1 or r.json()['id'] == 2
r = requests.get(categories_url + '/1/daily?orientation=any')
assert r.json()['id'] == 1 or r.json()['id'] == 2


print('Checking history hasnt changed')
r = requests.get(history_url)
assert r.json() == his

print('Adding new colors to image 4')
data = {"colors_matched": [3, 1, 2]}
r = requests.put(images_url + '/4', json=data)
print_code_response(r)
assert r.status_code == 200

print('Check results')
r = requests.get(images_url + "/4")
print_code_response(r)
assert r.status_code == 200
data = r.json()
delete_key(data, 'mtime')
assert data == {
                'license': 1,
                'source': 'http://grass4.com',
                'thumbnail': 'http://grass.com/thumb',
                'colors_matched': [3, 1, 2],
                'resolution': {'width': 100, 'height': 100},
                'categories': [3, 4],
                'origin': 'origin_test',
                'votes': 39,
                'uid': '89ae384112b1afdf9bdaa9187a77750c',
                'id': 4,

                }
