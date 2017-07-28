import os
from datetime import datetime
from random import Random

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
