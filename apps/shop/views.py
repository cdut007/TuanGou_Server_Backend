# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception
from ilinkgo.config import image_path

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
        from sqls import sql_goods_list

        sql_goods_detail = sql_goods_list.format(**{
            'group_buy_id': request.GET['group_buy_id'],
            'image_prefix': image_path()
        })

        cursor = connection.cursor()
        cursor.execute(sql_goods_detail)
        goods_list = dict_fetch_all(cursor)

        data = {
            'goods_list': goods_list,
            'group_buy_id': request.GET['group_buy_id']
        }

        return Response(format_body(1, 'Success', data))


class ClassifyView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_merchant_classify_group_buy_list_with_all_goods, sql_classify_info

        query = {
            'classify_id': request.GET['classify_id'],
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': image_path()
        }

        sql_classify_info = sql_classify_info.format(**query)
        sql_classify_group_buy_list = sql_merchant_classify_group_buy_list_with_all_goods % query

        cursor.execute(sql_classify_info)
        info = dict_fetch_all(cursor)[0]

        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_classify_group_buy_list)
        _list = dict_fetch_all(cursor)

        for item in _list:
            item['goods_list'] = json.loads(item['goods_list'])

        data = {
            'classify': info,
            'group_buy_list': _list,
        }

        return Response(format_body(1, 'Success', data))
