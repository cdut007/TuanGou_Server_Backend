from rest_framework.response import Response
from datetime import datetime

def format_body(code, message, data):
    res = {
        'code': code,
        'message': message,
        'data': data
    }
    return res

def utc_time_to_local_time(utc_time):
    time = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%SZ')
    return time.strftime('%Y-%m-%d %H:%M:%S')
