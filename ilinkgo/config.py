import os

class Config:
    def __init__(self):
        self.mode = os.environ.get('MODE', '')
        self.cwd = os.getcwd()
        self.wei_xin_mch_key_pem = self.cwd + '/other_file/apiclient_key.pem'
        self.wei_xin_mch_cert_pem = self.cwd + '/other_file/apiclient_cert.pem'
        self.domain = 'http://ailinkgo.ultralinked.com/'
        self._init_()

    def _init_(self):
        folder_name = self.cwd.split('/')[-1]
        if self.mode == 'TESTING'and folder_name == 'TuanGou_Server_Backend':
            self.live_env()
        elif self.mode == 'TESTING'and folder_name == 'TuanGou_Server_Backend_Testing':
            self.staging_env()
        elif self.mode == 'HOME' :
            self.home_env()
        else:
            self.dev_env()

    def live_env(self):
        self.mysql_db_name = 'ilinkgo'
        self.mysql_db_user = 'ilinkusr'
        self.mysql_db_password = 'ilinkusr123'
        self.image_file_path = '/var/www/html/ailinkgo/admin/images/'
        self.image_url_prefix = self.domain
        self.excel_file_path = '/var/www/html/ailinkgo/admin/excels/'
        self.excel_url_prefix = self.domain+'admin/excels/'
        self.server_run_addr = '47.90.86.229:3000'

    def staging_env(self):
        self.mysql_db_name = 'ilinkgo_test'
        self.mysql_db_user = 'ilinkusr'
        self.mysql_db_password = 'ilinkusr123'
        self.image_file_path = '/var/www/html/ailinkgo/adminTesting/images/'
        self.image_url_prefix = self.domain
        self.excel_file_path = '/var/www/html/ailinkgo/adminTesting/excels/'
        self.excel_url_prefix = self.domain+'adminTesting/excels/'
        self.server_run_addr = '47.90.86.229:3001'

    def dev_env(self):
        self.mysql_db_name = 'ilinkgo'
        self.mysql_db_user = 'root'
        self.mysql_db_password = '1234567a'
        self.image_file_path = '/usr/local/nginx/html/ilinkgo/admin/images/'
        self.image_url_prefix = 'http://www.ailinkgo.demo/'
        self.excel_file_path = '/usr/local/nginx/html/ilinkgo/admin/excels/'
        self.excel_url_prefix = 'http://www.ailinkgo.demo/admin/excels/'
        self.server_run_addr = '192.168.222.128:3000'

    def home_env(self):
        self.mysql_db_name = 'ilinkgo'
        self.mysql_db_user = 'root'
        self.mysql_db_password = '1234567a'
        self.image_file_path = '/usr/local/nginx_1.10.3/html/ailinkgo/admin/images/'
        self.image_url_prefix = 'http://www.ailinkgo.demo/'
        self.excel_file_path = '/usr/local/nginx_1.10.3/html/ailinkgo/admin/excels/'
        self.excel_url_prefix = 'http://www.ailinkgo.demo/admin/excels/'
        self.server_run_addr = '192.168.222.128:3000'


class StatusCode:
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
    orderEmpty = 17
    GroupBuyingNotEnd = 18
    NoBlankRp = 19
    RpLinkFailed = 22
    ThreeTimesToday = 23




