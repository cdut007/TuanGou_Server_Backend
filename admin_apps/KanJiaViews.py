# _*_ coding:utf-8 _*_
import json, uuid
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from ilinkgo.settings import conf
from utils.common import format_body, dict_fetch_all, raise_general_exception
from utils.common import sql_limit, sql_count, save_images

from apps.kanjia.models import KanJiaActivity


class CreateKanJiaActivity(APIView):
    @raise_general_exception
    def post(self, request):
        return Response(format_body(1, 'Success', ''))


class KanJiaList(APIView):
    @raise_general_exception
    def get(self, request):
        from KanJiaSqls import sql_kan_jia_list
        sql_kan_jia_list = sql_kan_jia_list.format(
            _image_prefix = conf.image_url_prefix,
            _limit = sql_limit(request)
        )
        cursor = connection.cursor()
        cursor.execute(sql_kan_jia_list)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'list': data}))


class KanJiaDetail(APIView):
    @raise_general_exception
    def get(self, request):
        from KanJiaSqls import sql_kan_jia_detail

        sql_kan_jia_detail = sql_kan_jia_detail.format(activity_id=request.GET['activity_id'])

        cursor = connection.cursor()
        cursor.execute(sql_kan_jia_detail)
        detail = dict_fetch_all(cursor)[0]
        detail['goods_image'] = [ {'id': 1, 'url': conf.image_url_prefix+detail['goods_image']} ]
        return Response(format_body(1, 'Success', {'detail': detail}))


class KanJiaSave(APIView):
    @raise_general_exception
    def post(self, request):
        info = request.data
        if info.has_key('activity_id'):
            activity = KanJiaActivity.objects.filter(activity_id=info['activity_id']).first()
        else:
            activity = KanJiaActivity()

        activity.title = info['title']
        if request.FILES.has_key('image'):
            activity.goods_image = save_images(request.FILES['image'], 'KanJia', create_thumbnail=False)
        activity.original_price = info['original_price']
        activity.activity_price = info['activity_price']
        activity.exchange_price = info['exchange_price']
        activity.max_kj_money = info['max_kj_money']
        activity.min_kj_money = info['min_kj_money']
        activity.goods_description = info['goods_description']
        activity.end_time = info['end_time']
        activity.quantity = info['quantity']
        activity.activity_description = info['activity_description']
        activity.activity_introduction = info['activity_introduction']
        activity.purchase_limitation = info['purchase_limitation']
        activity.need_subscribe = info['need_subscribe']
        activity.create_on = datetime.now()
        activity.save()

        return Response(format_body(1, 'Success', ''))