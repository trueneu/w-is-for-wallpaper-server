# W is for Wallpaper

## Disclaimer

This is a now-discontinued project "The Wall!", a Windows wallpaper manager with daily paper rotation support, wallpaper categories, sync between devices (desktop, mobile, watch) etc, server side. It was not intended for open source release in the first place, but in case someone's interested in the source code, here it is.
Code was actually written 2 years ago, so it's obviously shitty.

Distributed under GLWTPL. See LICENSE.txt or visit https://github.com/me-shaon/GLWTPL/blob/9d512d41b56f4cbed263e84571867d822af1ca25/NSFW_LICENSE .

It's up to you to setup it and install it. Database structure can be found under `tests` directory.

Godspeed!

### IMPLEMENTED

#### GETS:

- `/api/v1/images`
- `/api/v1/images/category/<category_id>`
- `/api/v1/images/<image_id>`
- `/api/v1/images/<image_id>/coords`
- `/api/vi/images/history?since=date`
- `/api/vi/images/count_newest_by_cat?since=date&categories=<comma separated list>` (if categories omitted, returns for
 all categories)
- `/api/v1/images/top?amount=(int)x`
- `/api/v1/images/random?orientation=[album|any]&category=<category_id>&color=<color_id>`  (default orientation is album; 
if category is omitted, it's synonym for all categories; if color is omitted, 
it's synonym for all colors)
- `/api/v1/licenses`
- `/api/v1/licenses/<license_id>`
- `/api/v1/licenses/history?since=date`
- `/api/v1/categories`
- `/api/v1/categories/<category_id>`
- `/api/v1/categories/history?since=date`
- `/api/v1/colors`
- `/api/v1/colors/<color_id>`
- `/api/v1/colors/history?since=date`
- `/api/v1/history?since=<date>`
- `/api/v1/categories/<category_id>/daily?type=[main|sec]&orientation=[album|any]&before=<datetime string>` (before 
is omitted, defaults to now)

#### POSTS:
- `/api/v1/images`
- `/api/v1/licenses`
- `/api/v1/categories`
- `/api/v1/colors`
- `/api/v1/categories/<category_id>/daily?type=[main|sec]&orientation=[album|any]`
- `/api/v1/categories/<category_id>/daily/rotate?orientation=[any|portrait]`
- `/api/v1/categories/rotate_dailies`

#### DELETES:
- `/api/v1/images`
- `/api/v1/licenses`
- `/api/v1/categories`
- `/api/v1/colors`
- `/api/v1/categories/<category_id>/daily?type=[main|sec]&orientation=[album|any]`

#### PUTS:
- `/api/v1/images/top` - modifies rating coefficients, recalculates all images' ratings
- `/api/v1/images/<image_id>/vote_up`
- `/api/v1/images/<image_id>/vote_down`
- `/api/v1/images`
- `/api/v1/licenses`
- `/api/v1/categories`
- `/api/v1/colors`
- `/api/v1/categories/<category_id>/daily?type=[main|sec]&orientation=[album|any]`
- `/api/v1/categories/<category_id>/daily/rotate?orientation=[any|portrait]`
- `/api/v1/categories/rotate_dailies`

### Examples
- Read all categories

  GET `/api/v1/categories`

- Write a category

  POST `/api/v1/categories`, payload == `{'name': 'Macro'}`

- Modify a category

  PUT `/api/v1/categories/1`, `{'name': 'MacroHooyacro'}`

- Delete a category

  DELETE `/api/v1/categories/1`

- Read raw history since 1st Jan, 2016

  GET `/api/v1/history`

- Read raw history since 2nd Jan, 2016, 14:00:00

  GET `/api/v1/history?since=2016-01-02T14:00:00`

  **ALL TIMES ARE IN UTC, ISO FORMAT**

- Read categories history since 10th Dec, 2016, 01:23:45

  GET `/api/v1/categories/history?since=2016-12-10T01:23:45`

### Data formats

- Category:

  `{'name': str, 
    'id': uid, 
    'image_id_cover': image uid OR absent if NULL}`

  Required fields for POST: `name`

- Color:

 `{'name': str, 'id': uid, 'r', 'g', 'b': unsigned short int}`
 
  Required fields for POST: `name`

- License:

  `{'name': str, 'url': str, 'id': uid}`
  
  Required fields for POST: `name`, `url`

- Image:

      {'categories': [list of category uids], 
       'thumbnail': str, 
       'source': str, 
       'id': uid, 
       'colors_matched': [list of color ids],
       'resolution': {'width': int, 'height': int}, 
       'mtime': date_created, 
       'license': license_id,
       'uid': unique_hash, 
       'origin': str, 
       'votes': int
      }
      
  Required fields for POST: `colors_matched`, `license`, `source`, `thumbnail`,
                         `resolution`, `categories`, `origin`


- Daily image (POST/PUT):

  `{'image_id': int}`
  
  GET returns the image info or 404 if there's no daily image.

### Test cases

All

- Read all with empty list
- Read all with non-empty list

Categories

- Add proper
- Read non-existent
- Read by id
- Read history since date
- Read history since date after deleting/modifying non-existent
- Delete proper
- Delete non-existent
- Modify proper
- Modify non-existent
- Daily images rotate/set

Colors

- Add proper
- Read by id
- Read non existent
- Modify
- Delete
- Read history since date
- Read history after modify/delete
- Delete linked

Licenses

- Add proper
- Add without a needed field
- Read by id
- Read non existent
- Modify
- Delete
- Read history since date
- Read history after modify/delete
- Delete linked

Images

- Add proper
- Add a duplicate by hash
- Read by id
- Modify correctly (plus modifying categories)
- Modify adding a non-existing category
- Modify source without modifying uid, uid gets changed
- Read history after modifying
- Delete
- Read history after deleting
- Get newest images since date by category
- Vote up/down

History

- Read raw
- Read raw since date

