import os

class StatusCode():
    TokenNeeded = -1
    TokenExpired = -2
    TokenInvalid = -3
    ObjectDoesNotExist = 0
    Success = 1
    ErrorParams = 2
    IsNotAgent = 3
    hasRecord = 4
    KeyError = 6
    OrderEmpty = 7
    NoHttpMethod = 10
    MysqlError = 11
    StockOutOfRange = 12
    NoThisOption = 13
    IndexError = 14
    JsApiConfigError = 15
    SaveImageFail = 16


def mysql_config():
    """load configuration"""
    mode = os.environ.get('MODE', '')
    dir_name = os.getcwd().split('/')[-1]

    if mode == 'PRODUCTION':
        mysql_config = {
            'name': 'ilinkgo',
            'user': 'ilinkusr',
            'password': 'ilinkusr123',
        }
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend':
       mysql_config = {
            'name': 'ilinkgo',
            'user': 'ilinkusr',
            'password': 'ilinkusr123',
       }
    elif mode == 'TESTING' and dir_name == 'TuanGou_Server_Backend_Testing':
        mysql_config = {
            'name': 'ilinkgo_test',
            'user': 'ilinkusr',
            'password': 'ilinkusr123',
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
    dir_name = os.getcwd().split('/')[-1]

    if mode == 'PRODUCTION':
        path = ''
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend':
        path = 'http://www.ailinkgo.com:3000/'
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend_Testing':
        path = 'http://www.ailinkgo.com:3001/'
    elif mode == 'HOME':
        path = 'http://192.168.239.129:8000/'
    else:
        path = 'http://192.168.222.128:3000/'

    return path

def image_path_v2():
    """load configuration"""
    mode = os.environ.get('MODE', '')
    dir_name = os.getcwd().split('/')[-1]

    if mode == 'PRODUCTION':
        path = ''
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend':
        path = 'http://www.ailinkgo.com:3000/'
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend_Testing':
        path = 'http://www.ailinkgo.com:3001/'
    elif mode == 'HOME':
        path = 'http://www.ailinkgo.demo/admin/images/'
    else:
        path = 'http://www.ailinkgo.demo/admin/images/'

    return path

def images_save_base_path():
    mode = os.environ.get('MODE', '')
    dir_name = os.getcwd().split('/')[-1]

    if mode == 'PRODUCTION':
        path = ''
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend':
        path = ''
    elif mode == 'TESTING'and dir_name == 'TuanGou_Server_Backend_Testing':
        path = ''
    elif mode == 'HOME':
        path = '/usr/local/nginx_1.10.3/html/ailinkgo/admin/images/'
    else:
        path = '/usr/local/nginx/html/ilinkgo/admin/images/'
    return path

def web_link():
    return 'http://www.ailinkgo.com/'


