# _*_ coding: utf-8 _*_
import functools

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from rest_framework.response import Response

from ilinkgo.settings import SECRET_KEY
from utils.common import format_body

class Authentication():
    @staticmethod
    def generate_auth_token(user_id, expiration=60480000):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': user_id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return -2
        except BadSignature:
            return -3
        return  data['id']

    @staticmethod
    def token_required(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kargs):
            if  not request._request.META.has_key('HTTP_AUTHORIZATION'):
                return Response(format_body(-1, 'Authentication token needed', ''))
            token = request._request.META['HTTP_AUTHORIZATION']
            wrapper.user_id =Authentication.verify_auth_token(token)
            if wrapper.user_id == -2:
                return Response(format_body(-2, 'Authentication token expired', ''))
            elif wrapper.user_id == -3:
                return Response(format_body(-3, 'Authentication token invalid', ''))
            return func(self, request, *args, **kargs)
        return wrapper