import os
import functools
from datetime import datetime
from random import Random

from rest_framework.response import Response
from django.db.models import ObjectDoesNotExist
from django.db import OperationalError


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
    "Returns all rows from a cursor as a dict"
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
            return Response(format_body(2, 'Params error', e.message))
        except ObjectDoesNotExist as e:
            return Response(format_body(6, 'Key value error', e.message))
        except IndexError as e:
            return Response(format_body(14, 'index error', e.message))
        except OperationalError as e:
            return Response(format_body(11, 'Mysql error', e.message))
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
