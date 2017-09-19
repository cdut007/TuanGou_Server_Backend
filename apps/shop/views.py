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


class GoodsView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()
        if request.GET['option'] == 'detail':
            from sqls import sql_goods_detail, sql_goods_detail_related

            sql_goods_detail = sql_goods_detail.format(**{
                'goods_id': request.GET['goods_id'],
                'image_prefix': image_path()
            })
            sql_goods_detail_related = sql_goods_detail_related.format(**{
                'goods_id': request.GET['goods_id'],
                'image_prefix': image_path()
            })

            cursor.execute(sql_goods_detail)
            goods_detail = dict_fetch_all(cursor)[0]
            goods_detail['images'] = json.loads(goods_detail['images'])

            cursor.execute(sql_goods_detail_related)
            goods_detail_related = dict_fetch_all(cursor)

            return Response(format_body(1, 'Success', {'goods_detail': goods_detail, 'group_buy': goods_detail_related}))

        elif request.GET['option'] == 'list':
            return Response(format_body(1, 'Success', {'goods_detail': 1, 'group_buy': 1}))

        else:
            return Response(format_body(13, 'No this option', ''))