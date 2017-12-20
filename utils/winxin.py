# _*_ coding:utf-8 _*_
import urllib, urllib2, json, hashlib, time, requests, re
from datetime import datetime
from common import random_str
from ilinkgo.settings import conf
from apps.other.models import WinXinCache

class WeiXinAPI:
    def __init__(self):
        self.app_id = 'wx3dfb837875e773af'
        self.secret = '8f124947d450ee56458828481d183889'
        self.mch_key = 'okljv0R6houqibewuLKYFhLU8kcLU8kc'
        self.mch_id = '1450506702'
        self.xml_header = {'Content-Type': 'application/xml'}

    def basal_access_token(self):
        u"""公众号的全局唯一接口调用凭据"""
        params = dict()
        params['appid'] = self.app_id
        params['secret'] = self.secret
        params['grant_type'] = 'client_credential'
        url = 'https://api.weixin.qq.com/cgi-bin/token?' + urllib.urlencode(params)
        response = urllib2.urlopen(urllib2.Request(url))
        return json.loads(response.read())

    @staticmethod
    def js_api_ticket(access_token):
        u"""公众号用于调用微信JS接口的临时票据"""
        params = dict()
        params['access_token'] = access_token
        params['type'] = 'jsapi'
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?' + urllib.urlencode(params)
        response = urllib2.urlopen(urllib2.Request(url))
        return json.loads(response.read())

    @staticmethod
    def js_api_config(js_api_ticket, url):
        noncestr = random_str(10)
        timestamp = int(time.time())
        string1 = 'jsapi_ticket={0}&noncestr={1}&timestamp={2}&url={3}'.format(
            js_api_ticket,noncestr,timestamp,url)
        signature = hashlib.sha1(string1).hexdigest()

        return {
            'noncestr': noncestr,
            'timestamp': timestamp,
            'url': url,
            'signature': signature
        }

    def website_authorization_access_token(self,code):
        u"""网页授权access_token"""
        params = dict()
        params['appid'] = self.app_id
        params['secret'] = self.secret
        params['code'] = code
        params['grant_type'] = 'authorization_code'
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' + urllib.urlencode(params)
        response = urllib2.urlopen(urllib2.Request(url))
        return json.loads(response.read())

    @staticmethod
    def website_user_info(access_token, open_id):
        u"""使用网页授权access_token"""
        params = dict()
        params['access_token'] = access_token
        params['openid'] = open_id
        params['lang'] = 'zh_CN'
        url = ' https://api.weixin.qq.com/sns/userinfo?' + urllib.urlencode(params)
        response = urllib2.urlopen(urllib2.Request(url))
        return json.loads(response.read())

    def get_wei_xin_basal_access_token(self):
        cached = WinXinCache.objects.filter(cache_key='access_token')
        if cached:
            cached = cached[0]
            if cached.expire_date > datetime.now():
                return cached.cache_value
            else:
                cached.delete()

        data = self.basal_access_token()
        if data.has_key('access_token'):
            expire_date = time.localtime(int(time.time()) + data['expires_in'])
            expire_date = time.strftime('%Y-%m-%d %H:%M:%S', expire_date)
            q = WinXinCache(
                cache_key='access_token',
                cache_value=data['access_token'],
                expire_date=expire_date
            )
            q.save()
            return data['access_token']
        else:
            return 'error'

    def get_wei_xin_js_api_ticket(self, access_token):
        cached = WinXinCache.objects.filter(cache_key='js_api_ticket')
        if cached:
            cached = cached[0]
            if cached.expire_date > datetime.now():
                return cached.cache_value
            else:
                cached.delete()

        data = self.js_api_ticket(access_token)
        if data.has_key('ticket'):
            expire_date = time.localtime(int(time.time()) + data['expires_in'])
            expire_date = time.strftime('%Y-%m-%d %H:%M:%S', expire_date)
            q = WinXinCache(
                cache_key='js_api_ticket',
                cache_value=data['ticket'],
                expire_date=expire_date
            )
            q.save()
            return data['ticket']
        else:
            return 'error'

    def get_wei_xin_js_sdk_config(self, url):
        access_token = self.get_wei_xin_basal_access_token()
        if access_token == 'error':
            return 'error'

        ticket = self.get_wei_xin_js_api_ticket(access_token)
        if ticket == 'error':
            return 'error'

        config = self.js_api_config(ticket, url)
        return config

    def push_notice(self, data):
        access_token = self.get_wei_xin_basal_access_token()
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token="+access_token

        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(url=url, headers=headers, data=json.dumps(data))
        response = urllib2.urlopen(request)

    def send_red_pack(self):
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'
        payload = {
            'nonce_str': random_str(random_length=20),
            'mch_billno': '0010010404201411170000b',
            'mch_id': self.mch_id,
            'wxappid': self.app_id,
            'send_name': 'ilinkgo',
            're_openid': 'okljv0R6hou-qibewuLKYFhLU8kc',
            'total_amount': 100,
            'total_num': 1,
            'wishing': 'havefun',
            'client_ip': '127.0.0.1',
            'act_name': 'happynewyear',
            'remark': 'happynewyear',
            'scene_id': 'PRODUCT_1'
        }
        payload['sign'] = self.sign(payload)

        xml_data = WeiXinXml.json2xml(payload)
        res = requests.post(
            url=url,
            data=xml_data,
            headers=self.xml_header,
            cert=(conf.wei_xin_mch_cert_pem, conf.wei_xin_mch_key_pem)
        )
        res_json = WeiXinXml.xml2json(res.text)
        return res_json

    def sign(self,payload):
        sorted_keys = sorted(payload)
        strmd = ''
        for key in sorted_keys:
            if payload[key]:
                strmd += key + '=' + unicode(payload[key]) + '&'
        strmd += "key=" + self.mch_key
        m = hashlib.md5()
        m.update(strmd)
        sw = str(m.hexdigest()).upper()
        return sw


class WeiXinXml:
    def __init__(self):
        pass

    @staticmethod
    def json2xml(org_json):
        xml = '<xml>\n'
        for key, val in org_json.items():
            xml += '<{_key}><![CDATA[{_val}]]></{_key}>\n'.format(_key=key, _val=val)
        xml += '</xml>'
        return xml

    @staticmethod
    def xml2json(org_xml):
        xml_list = str(org_xml).splitlines()
        xml_list = xml_list[1:-1]

        pattern_key = re.compile('<(\w+)>')
        pattern_val1 = re.compile('CDATA\[(.+?)]')
        pattern_val2 = re.compile('>(\w+)<')

        res = dict()
        for line in xml_list:
            key = pattern_key.findall(line)
            key = key[0]
            val = pattern_val1.findall(line)
            if not val:
                val = pattern_val2.findall(line)
            val = val[0]
            res[key] = val

        return res




