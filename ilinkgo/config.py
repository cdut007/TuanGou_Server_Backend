import os

class StatusCode():
    TokenNeeded = -1
    TokenExpired = -2
    TokenInvalid = -3
    Success = 1
    ErrorParams = 2
    IsNotAgent = 3
    hasRecord = 4
    ObjectDoesNotExist = 5
    KeyError = 6



def mysql_config():
    """load configuration"""
    mode = os.environ.get('MODE', '')

    if mode == 'PRODUCTION':
        mysql_config = {
            'name': 'ilinkgo',
            'user': 'root',
            'password': 'pPt87G6c9FCG2117',
        }
    elif mode == 'TESTING':
       mysql_config = {
            'name': 'ilinkgo',
            'user': 'root',
            'password': 'pPt87G6c9FCG2117',
       }
    else:
        mysql_config = {
            'name': 'ilinkgo',
            'user': 'root',
            'password': '1234567a',
        }

    return mysql_config

def image_path():
    """load configuration"""
    mode = os.environ.get('MODE', '')

    if mode == 'PRODUCTION':
        path = ''
    elif mode == 'TESTING':
        path = 'http://47.88.139.113:3000/'
    else:
        path = 'http://192.168.222.128:3000/'

    return path


