import os, time, json
import functools
from datetime import datetime
from random import Random

from rest_framework.response import Response
from django.db.models import ObjectDoesNotExist
from django.db import OperationalError

from ilinkgo.config import images_save_base_path


def format_body(code, message, data):
    res = {
        'code': code,
        'message': message,
        'data': data
    }
    return res


def thumbnail(image_url):
    return os.path.splitext(image_url)[0] + '_thumbnail' + os.path.splitext(image_url)[1]


def utc_time_to_local_time(utc_time):
    time = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S')
    return time.strftime('%Y-%m-%d %H:%M:%S')


def random_str(random_length=5):
    string = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZ0123456789'
    for i in range(random_length):
        string += chars[ Random().randint(0, len(chars) - 1)]
    return string


def dict_fetch_all(cursor):
    """Returns all rows from a cursor as a dict"""
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def raise_general_exception(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kargs):
        try:
            return func(self, request, *args, **kargs)
        except KeyError as e:
            return Response(format_body(2, 'Params error', {'message': e.message, 'args': e.args}))
        except ObjectDoesNotExist as e:
            return Response(format_body(6, 'Key value error', {'message': e.message, 'args': e.args}))
        except IndexError as e:
            return Response(format_body(14, 'index error', {'message': e.message, 'args': e.args}))
        except OperationalError as e:
            return Response(format_body(11, 'Mysql error', {'message': e.message, 'args': e.args}))
        except Exception as e:
            return Response(format_body(19, 'Other error', {'message': e.message, 'args': e.args}))
    return wrapper


def sql_limit(request):
    if request.GET.has_key('pageSize'):
        pageSize = request.GET['pageSize']
    else:
        pageSize = 10

    if request.GET.has_key('currentPage'):
        currentPage = request.GET['currentPage']
    else:
        currentPage = 1

    start = (int(currentPage) - 1) * int(pageSize)

    _limit = "LIMIT " + str(start) + ", " + str(pageSize)

    return _limit


def sql_count(sql):
    return "SELECT COUNT(*) AS count FROM(" + sql + ") AS temp"


def get_owner(user_id):
    if str(user_id).startswith('admin_'):
        owner = user_id
    else:
        owner = 'app_' + str(user_id)
    return owner


def save_images(image_file, destination='Goods', create_thumbnail=False):
    try:
        sub_path = destination + "/{}-{}/".format(
            time.strftime('%Y'),
            time.strftime('%m')
        )
        path = images_save_base_path() + sub_path

        if not os.path.exists(path):
            os.makedirs(path)

        temp = image_file.name.split('.')
        image_name = temp[0] + '_' + random_str() + '.' + temp[-1]

        destination = open(path + image_name, 'wb+')
        for chunk in image_file.chunks():
            destination.write(chunk)
            destination.close()

        if create_thumbnail:
            from PIL import Image
            origin_image = image_name.split('.')
            image_thumbnail = path + origin_image[0] + '_thumbnail.' + origin_image[1]
            im = Image.open(image_file)
            im.thumbnail((230, 230))
            im.save(image_thumbnail, im.format)

    except Exception as e:
        return False
    return '/'.join(images_save_base_path().split('/')[-3:])+sub_path+image_name

