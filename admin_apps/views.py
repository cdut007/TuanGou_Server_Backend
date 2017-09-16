# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception
from ilinkgo.config import image_path
from market.models import GroupBuyGoods
from iuser.models import GenericOrder

from iuser.Authentication import Authentication


class LogInView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        data = {
            'name': 'admin',
            'role': 'admin',
            'avatar': 'http://img05.tooopen.com/images/20160109/tooopen_sy_153858412946.jpg'
        }
        return Response(format_body(1, 'success', data))

    @raise_general_exception
    def post(self, request):
        from django.contrib.auth.models import User

        user = User.objects.get(username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response(format_body(6, 'password wrong', ''))

        token = Authentication.generate_auth_token(user.id, 604800)
        return Response(format_body(1, 'success', {'token': token}))
