import urllib
import urllib2
import json
def code_to_access_token(code):
    """
     https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code 
    :return: 
    """
    params = dict()
    params['appid'] = 'wx3dfb837875e773af'
    params['secret'] = '8f124947d450ee56458828481d183889'
    params['code'] = code
    params['grant_type'] = 'authorization_code'
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' + urllib.urlencode(params)
    response = urllib2.urlopen(urllib2.Request(url))
    return json.loads(response.read())

def access_token_to_user_info(access_token, open_id):
    params = dict()
    params['access_token'] = access_token
    params['openid'] = open_id
    params['lang'] = 'zh_CN'
    url = ' https://api.weixin.qq.com/sns/userinfo?' + urllib.urlencode(params)
    response = urllib2.urlopen(urllib2.Request(url))
    return json.loads(response.read())

