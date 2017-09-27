# _*_ coding:utf-8 _*_
import urllib
import urllib2
import json
import hashlib
import time
from common import random_str


class WeiXinAPI:
    def __init__(self):
        self.app_id = 'wx3dfb837875e773af'
        self.secret = '8f124947d450ee56458828481d183889'

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
    def js_api_config(js_api_ticket):
        noncestr = random_str(10)
        timestamp = time.time()
        url = 'http://www.ailinkgo.com/'
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

    @staticmethod
    def get_wei_xin_basal_access_token():
        return 'paNAi-ikq2QBhEtjgu5OKcVGT1Vj3WpUnpAzSKdXFW-3aeUZMN7kl45gV2Sosox_jYB8-6XwJLbWwfdzGtfxRHBxeqmOQZQDghAYPR3OBdCxj8y8UuLE8-tVglksfO3GJRUaAEAAIL'

    def get_wei_xin_js_sdk_config(self):
        ticket = 'HoagFKDcsGMVCIY2vOjf9qGYYgyqaWgWZ6RmHt4w2NdhTEFzUyZW0nAeUCu-Y1iVA-wLIuxgdSsovdLVd54cpw'
        config = self.js_api_config(ticket)
        return config

