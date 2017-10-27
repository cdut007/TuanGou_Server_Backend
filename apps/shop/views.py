# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit
from ilinkgo.config import image_path

from iuser.Authentication import Authentication


class MerchantGoodsDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_goods_detail, sql_merchant_goods_detail_related, sql_goods_classify
        from sqls import sql_goods_purchased_user

        query = {
            'goods_id': request.GET['goods_id'],
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': image_path(),
            'access_user': Authentication.access_user(request)
        }

        sql_goods_detail = sql_goods_detail % query
        sql_goods_detail_related = sql_merchant_goods_detail_related.format(**query)
        sql_goods_classify = sql_goods_classify.format(**query)

        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_classify)
        classify = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_detail_related)
        goods_detail_related = dict_fetch_all(cursor)

        goods_detail['group_buying'] = json.loads(goods_detail['group_buying'])
        goods_detail['group_buying']['goods_list'] = goods_detail_related
        goods_detail['classify'] = classify
        goods_detail['images'] = json.loads(goods_detail['images'])

        sql_goods_purchased_user = sql_goods_purchased_user.format(
            goods_id=request.GET['goods_id'],
            _limit='LIMIT 0, 6'
        )

        cursor.execute(sql_goods_purchased_user)
        purchased_user = dict_fetch_all(cursor)
        goods_detail['purchased_user'] = purchased_user

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))


class MerchantGoodsPurchasedUserView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_goods_purchased_user
        cursor = connection.cursor()

        sql_goods_purchased_user = sql_goods_purchased_user.format(
            goods_id=request.GET['goods_id'],
            _limit=sql_limit(request)
        )

        cursor.execute(sql_goods_purchased_user)
        purchased_user = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'purchased_user': purchased_user}))


class MerchantGoodsListView(APIView):
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


class MerchantClassifyView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_classify_info
        from sqls import sql_merchant_classify_group_buy_list_with_all_goods_v2

        query = {
            'classify_id': request.GET['classify_id'],
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': image_path(),
            'access_user': Authentication.access_user(request)
        }

        sql_classify_info = sql_classify_info.format(**query)
        sql_classify_group_buy_list = sql_merchant_classify_group_buy_list_with_all_goods_v2 % query

        cursor.execute(sql_classify_info)
        info = dict_fetch_all(cursor)[0]

        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_classify_group_buy_list)
        _list = dict_fetch_all(cursor)

        for item in _list:
            item['goods_list'] = json.loads(item['goods_list'].replace('"[', '[').replace(']"', ']'))

        data = {
            'classify': info,
            'group_buy_list': _list,
        }

        return Response(format_body(1, 'Success', data))
