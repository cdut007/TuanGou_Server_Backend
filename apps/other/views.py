# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, raise_general_exception
from utils.winxin import WeiXinAPI
from ilinkgo.config import image_path

from iuser.Authentication import Authentication


class WeiXinJsSdkConfigView(APIView):
    @raise_general_exception
    def get(self, request):
        wei_xin_api = WeiXinAPI()
        config = wei_xin_api.get_wei_xin_js_sdk_config()
        if config == 'error':
            return Response(format_body(15, 'Fail', 'error'))
        return Response(format_body(1, 'Success', config))