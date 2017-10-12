# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception
from ilinkgo.config import image_path_v2
from utils.common import sql_limit, sql_count, save_images

from market.models import Goods

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
            '_image_prefix': 'http://www.ailinkgo.demo/',
            '_where': '',
            '_order_by': 'ORDER BY a.id DESC',
            '_limit': sql_limit(request)
        })
        _sql_goods_list_count = sql_count(sql_goods_list.format(**{
            '_image_prefix': 'http://www.ailinkgo.demo/',
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

        sql_goods_detail = sql_goods_detail % {'goods_id': request.GET['goods_id'], 'image_prefix': 'http://www.ailinkgo.demo/'}

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        goods_detail['images'] = json.loads(goods_detail['images'])

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))


class ProductCreateView(APIView):
    @raise_general_exception
    def post(self, request):
        from sqls import sql_insert_goods_gallery

        goods = Goods(
            name=request.data['name'],
            desc=request.data['desc']
        )
        goods.save()

        insert_values = ""
        is_primary = 1
        for image in sorted(request.FILES):
            image_path = 'admin/images/' + save_images(request.FILES[image], 'Goods', create_thumbnail=True)
            insert_values += "('{0}', '{1}', '{2}', '{3}'),\n".format(image_path,is_primary,datetime.now(),goods.id)
            is_primary = 0

        sql_insert_goods_gallery = sql_insert_goods_gallery.format(values=insert_values[0:-2])

        cursor = connection.cursor()
        cursor.execute(sql_insert_goods_gallery)

        return Response(format_body(1, 'Success', ''))


class ProductUpdateView(APIView):
    @raise_general_exception
    def post(self, request):
        goods = Goods.objects.get(id=request.data['product_id'])
        goods.name = request.data['name']
        goods.desc = request.data['desc']
        goods.save()

        cursor = connection.cursor()

        if request.FILES:
            from sqls import  sql_insert_goods_gallery
            insert_values = ""
            for image in sorted(request.FILES):
                image_path = 'admin/images/' + save_images(request.FILES[image], 'Goods', create_thumbnail=True)
                insert_values += "('{0}', '{1}', '{2}', '{3}'),\n".format(image_path, 0, datetime.now(), goods.id)
            sql_insert_goods_gallery = sql_insert_goods_gallery.format(values=insert_values[0:-2])
            cursor.execute(sql_insert_goods_gallery)

        if request.data['detImg']:
            from sqls import sql_delete_goods_gallery, sql_update_gallery_primary
            sql_delete_goods_gallery = sql_delete_goods_gallery.format(detImg=request.data['detImg'])
            sql_update_gallery_primary = sql_update_gallery_primary.format(goods_id=goods.id)
            cursor.execute(sql_delete_goods_gallery)
            cursor.execute(sql_update_gallery_primary)

        return Response(format_body(1, 'Success', ''))


class ImageUploadView(APIView):
    def post(self, request):
        image = request.FILES['image']
        image_path = save_images(image, 'GoodsDetail')
        if image_path:
            url = image_path_v2() + image_path
            return Response(format_body(1, 'Success', url))
        return Response(format_body(16, 'Fail', ''))


class CleanImages(APIView):
    def get(self, request):
        import os
        sql = """
        SELECT
            SUBSTRING_INDEX(image, '/' ,- 1) AS images
        FROM
            market_goodsgallery
        WHERE
            image LIKE '%/2017-09/%'
	"""
        cursor = connection.cursor()
        cursor.execute(sql)

        images = cursor.fetchall()
        images = [i[0] for i in  images]

        _dir = '/usr/local/nginx_1.10.3/html/ailinkgo/admin/images/Goods/2017-09'

        files = os.listdir(_dir)
        for file in files:
            try:
                if '_thumbnail.' not in file and  file not in images:
                    path = os.path.join(_dir, file)
                    thumbnail = file.split('.')[0] + '_thumbnail.' + file.split('.')[-1]
                    path_thumbnail = os.path.join(_dir, thumbnail)
                    os.remove(path)
                    os.remove(path_thumbnail)
            except OSError :
                continue

        return Response(format_body(1, 'Success', ''))


class ProductSearchView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_product_search

        cursor = connection.cursor()

        sql_product_search = sql_product_search.format(
            _image_prefix = 'http://www.ailinkgo.demo/',
            _keyword = request.GET['keyword']
        )

        cursor.execute(sql_product_search)

        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', data))


class GroupBuyingListView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_group_buying_list

        cursor = connection.cursor()
        cursor.execute(sql_group_buying_list)
        sql_goods_buying_list_count = sql_count(sql_group_buying_list)
        data = dict_fetch_all(cursor)

        cursor.execute(sql_goods_buying_list_count)
        count = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {
            'groupbuying_list': data,
            'paged': {'total': count[0]['count']}
        }))




