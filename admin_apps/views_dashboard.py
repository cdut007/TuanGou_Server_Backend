# _*_ coding:utf-8 _*_
import json, uuid
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception
from ilinkgo.config import image_path
from utils.common import sql_limit, sql_count, save_images, get_owner

from market.models import Goods, GoodsClassify
from iuser.models import UserProfile, AgentOrder
from iuser.Authentication import Authentication


class GroupBuyingDoingView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls_dashboard import sql_group_buying_doing

        sql_group_buying_doing = sql_group_buying_doing.format(
            _image_prefix = 'http://www.ailinkgo.com/'
        )

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_group_buying_doing)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'group_buying': data}))