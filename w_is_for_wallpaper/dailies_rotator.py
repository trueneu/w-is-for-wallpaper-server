import os
import pickle
import random
from datetime import datetime
from w_is_for_wallpaper import responder

QUEUE_DIR = 'daily_queues'


def load_queue(path, category_id, orientation):
    queue_filename = '{}/{}_{}.pkl'.format(path, int(category_id), orientation)
    try:
        with open(queue_filename, 'rb') as f:
            unsafe_queue = pickle.load(f)
    except FileNotFoundError:
        unsafe_queue = None
    return unsafe_queue


def save_queue(path, category_id, orientation, queue):
    queue_filename = '{}/{}_{}.pkl'.format(path, int(category_id), orientation)
    with open(queue_filename, 'wb') as f:
        pickle.dump(queue, f, 0)


def update_queue(category_id, orientation, current_queue):
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

    if orientation == 'album':
        try:
            images = responder.get_images_full_info_by_category_id(category_id)
            album_images = [image for image in images
                            if image['resolution']['width'] > image['resolution']['height']]
        except TypeError:  # no images present
            return None

        all_images = album_images
        all_image_ids = [x['id'] for x in all_images]

    elif orientation == 'any':
        try:
            images = responder.get_images_full_info_by_category_id(category_id)
        except TypeError:  # no images present
            return None
        all_images = images
        all_image_ids = [x['id'] for x in all_images]

    unsafe_queue = current_queue
    if not unsafe_queue:
        unsafe_queue = all_image_ids

    if not unsafe_queue:
        return

    try:
        current_daily_image_id = responder.get_daily_image(category_id, 'main', orientation, now_str)['id']
    except responder.NotFoundException:
        current_daily_image_id = None

    queue = []
    for image_id in unsafe_queue:
        if image_id in all_image_ids:  # if an image from queue got deleted, it won't get in queue
            queue.append(image_id)

    if not current_daily_image_id:
        new_daily_image_queue_position = 0
    elif current_daily_image_id not in queue:  # daily image got deleted? holy shit!
        new_daily_image_queue_position = random.randint(0, len(queue) - 1)
    else:
        new_daily_image_queue_position = queue.index(current_daily_image_id) + 1
        if new_daily_image_queue_position >= len(queue):
            new_daily_image_queue_position = 0

    # inject new images in queue
    for image_id in all_image_ids:
        if image_id not in queue:
            queue.insert(new_daily_image_queue_position, image_id)

    # write new daily
    responder.modify_daily_image(category_id, 'main', orientation,
                                 {'image_id': queue[new_daily_image_queue_position]})

    return queue


def rotate_dailies(path, category_ids=None, orientations=None):
    if category_ids is None:
        category_ids = [x['id'] for x in responder.get_categories()]
    if orientations is None:
        orientations = ['album', 'any']

    for category_id in category_ids:
        for orientation in orientations:
            current_queue = load_queue(path, category_id, orientation)
            save_queue(path, category_id, orientation, update_queue(category_id, orientation, current_queue))


if __name__ == '__main__':
    queue_dir_full_path = os.path.join(os.path.dirname(__file__), QUEUE_DIR)
    try:
        os.mkdir(queue_dir_full_path)
    except FileExistsError:
        pass
    except OSError:
        exit(1)
    rotate_dailies(queue_dir_full_path)
