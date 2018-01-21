# _*_ coding:utf-8 _*_
import os, time, json
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage

from ilinkgo.settings import conf
from utils.gen_excel import order_excel
from utils.common import format_body, raise_general_exception, random_str, dict_fetch_all
from utils.winxin import WeiXinAPI
from apps.user.models import MerchantPushLog
from iuser.models import UserProfile
from market.models import GroupBuy
from utils.common import random_str

from iuser.Authentication import Authentication


class WxPayView(APIView):
    @raise_general_exception
    def post(self, request):
        wei_xin_api = WeiXinAPI()
        res = wei_xin_api.pay()
        return Response(format_body(1, 'Success', res))
