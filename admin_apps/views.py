# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit, sql_count
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


class ProductListView(APIView):
    # @Authentication.token_required
    # @raise_general_exception
    def get(self, request):
        from sqls import sql_goods_list

        _sql_goods_list = sql_goods_list.format(**{
            '_image_prefix': 'http://www.ailinkgo.com:3001/',
            '_where': '',
            '_order_by': 'ORDER BY a.id DESC',
            '_limit': sql_limit(request)
        })
        _sql_goods_list_count = sql_count(sql_goods_list.format(**{
            '_image_prefix': 'http://www.ailinkgo.com:3001/',
            '_where': '',
            '_order_by': '',
            '_limit': ''
        }))

        cursor = connection.cursor()

        cursor.execute(_sql_goods_list)
        product_list = dict_fetch_all(cursor)

        cursor.execute(_sql_goods_list_count)
        count = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {
            'product_list': product_list,
            'paged': {'total': count[0]['count']}
        }))


class ProductDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_goods_detail

        sql_goods_detail = sql_goods_detail % {'goods_id': request.GET['goods_id'], 'image_prefix': 'http://www.ailinkgo.com:3001/'}

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        goods_detail['images'] = json.loads(goods_detail['images'])

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))
