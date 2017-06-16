# _*_ coding: utf-8 _*_
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

class Authentication():
    # SECRET_KEY = 'h6#Tkd8kl$aY*sia&dfs_%6V3e'
    @staticmethod
    def generate_auth_token(user_id, expiration=604800):
        s = Serializer('h6#Tkd8kl$aY*sia&dfs_%6V3e', expires_in=expiration)
        return s.dumps({'id': user_id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('h6#Tkd8kl$aY*sia&dfs_%6V3e')
        try:
            data = s.loads(token)
        except SignatureExpired:
            return
        except BadSignature:
            return None
        return  data['id']