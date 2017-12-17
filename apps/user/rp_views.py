# _*_ coding:utf-8 _*_
import json, time,random
from decimal import Decimal
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit
from utils.winxin import WeiXinAPI
from ilinkgo.config import image_path
from market.models import GroupBuyGoods, GroupBuy
from iuser.models import GenericOrder, UserProfile
from models import UnpackRedPacketsLog
from  MySQLdb import escape_string
from iuser.Authentication import Authentication

class UnpackRedPacketsView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        receiver = UserProfile.objects.get(sharing_code=request.data['sharing_code'])
        unpack_user_id = self.post.user_id
        group_buying_id = request.data['group_buying_id']
        money = self.gen_rp_money()
        pass

    @staticmethod
    def gen_rp_money():
        return str(Decimal(random.uniform(0.2, 0.6)).quantize(Decimal('0.00')))


class RpOneDetailView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        receiver = UserProfile.objects.get(sharing_code=request.data['sharing_code'])
        unpack_user_id = self.post.user_id
        group_buying_id = request.data['group_buying_id']
        money = self.gen_rp_money()
        pass

