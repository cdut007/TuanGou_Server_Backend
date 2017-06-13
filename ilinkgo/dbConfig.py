import os


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

