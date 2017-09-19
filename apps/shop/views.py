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


class GoodsDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_goods_detail, sql_goods_detail_related, sql_goods_classify

        query = {
            'goods_id': request.GET['goods_id'],
            'image_prefix': image_path()
        }

        sql_goods_detail = sql_goods_detail.format(**query)
        sql_goods_detail_related = sql_goods_detail_related.format(**query)
        sql_goods_classify = sql_goods_classify.format(**query)

        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_classify)
        classify = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_detail_related)
        goods_detail_related = dict_fetch_all(cursor)

        goods_detail['group_buy'] = goods_detail_related
        goods_detail['classify'] = classify
        goods_detail['images'] = json.loads(goods_detail['images'])

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))


class GoodsListView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_goods_detail, sql_goods_detail_related, sql_goods_classify

        query = {
            'goods_id': request.GET['goods_id'],
            'image_prefix': image_path()
        }

        sql_goods_detail = sql_goods_detail.format(**query)
        sql_goods_detail_related = sql_goods_detail_related.format(**query)
        sql_goods_classify = sql_goods_classify.format(**query)

        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_classify)
        classify = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_detail_related)
        goods_detail_related = dict_fetch_all(cursor)

        goods_detail['group_buy'] = goods_detail_related
        goods_detail['classify'] = classify
        goods_detail['images'] = json.loads(goods_detail['images'])

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))


class ClassifyView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_classify_group_buy_first, sql_classify_group_buy_list, sql_classify_info

        query = {
            'classify_id': request.GET['classify_id'],
            'image_prefix': image_path()
        }

        sql_classify_info = sql_classify_info.format(**query)
        sql_classify_group_buy_list = sql_classify_group_buy_list.format(**query)
        sql_classify_group_buy_first = sql_classify_group_buy_first.format(**query)

        cursor.execute(sql_classify_info)
        info = dict_fetch_all(cursor)[0]

        cursor.execute(sql_classify_group_buy_list)
        list = dict_fetch_all(cursor)

        cursor.execute(sql_classify_group_buy_first)
        first = dict_fetch_all(cursor)

        data = {
            'classify': info,
            'group_buy_list': list,
            'group_buy_first': first
        }

        return Response(format_body(1, 'Success', data))
