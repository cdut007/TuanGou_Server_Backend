import os
from datetime import datetime

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
