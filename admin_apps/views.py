# _*_ coding:utf-8 _*_
import json
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all, raise_general_exception
from ilinkgo.config import image_path
from utils.common import sql_limit, sql_count, save_images

from market.models import Goods, GoodsClassify
from iuser.models import UserProfile
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

        token = Authentication.generate_auth_token('admin_'+str(user.id), 604800)
        return Response(format_body(1, 'success', {'token': token}))


class ProductListView(APIView):
    # @Authentication.token_required
    # @raise_general_exception
    def get(self, request):
        from sqls import sql_goods_list

        _sql_goods_list = sql_goods_list.format(**{
            '_image_prefix': image_path(),
            '_where': '',
            '_order_by': 'ORDER BY a.id DESC',
            '_limit': sql_limit(request)
        })
        _sql_goods_list_count = sql_count(sql_goods_list.format(**{
            '_image_prefix': image_path(),
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

        sql_goods_detail = sql_goods_detail % {'goods_id': request.GET['goods_id'], 'image_prefix': image_path()}

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]

        goods_detail['images'] = json.loads(goods_detail['images'])

        return Response(format_body(1, 'Success', {'goods_detail': goods_detail}))


class ProductCreateView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from sqls import sql_insert_goods_gallery

        if str(self.post.user_id).startswith('admin_'):
            owner = self.post.user_id
        else:
            owner = 'app_'+ self.post.user_id

        goods = Goods(
            name = request.data['name'],
            desc = request.data['desc'],
            default_price = request.data['default_price'],
            default_stock = request.data['default_stock'],
            default_unit = request.data['default_unit'],
            set = request.data['set'],
            created_by = owner
        )
        goods.save()

        insert_values = ""
        for index, image in enumerate(sorted(request.FILES)):
            is_primary = 1 if index==0 else 0
            img_path = save_images(request.FILES[image], 'Goods', create_thumbnail=True)
            insert_values += "('{0}', '{1}', '{2}', '{3}'),\n".format(img_path,is_primary,datetime.now(),goods.id)

        sql_insert_goods_gallery = sql_insert_goods_gallery.format(values=insert_values[0:-2])

        cursor = connection.cursor()
        cursor.execute(sql_insert_goods_gallery)

        return Response(format_body(1, 'Success', ''))


class ProductUpdateView(APIView):
    @raise_general_exception
    def post(self, request):
        goods = Goods.objects.get(id=request.data['goods_id'])
        goods.name = request.data['name']
        goods.desc = request.data['desc']
        goods.default_price = request.data['default_price']
        goods.default_stock = request.data['default_stock']
        goods.default_unit = request.data['default_unit']
        goods.set = request.data['set']
        goods.save()

        cursor = connection.cursor()

        if request.FILES:
            from sqls import  sql_insert_goods_gallery
            insert_values = ""
            for image in sorted(request.FILES):
                image_path = save_images(request.FILES[image], 'Goods', create_thumbnail=True)
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


class ProductSetUpdateView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from sqls import sql_product_set_update

        sql_product_set_update = sql_product_set_update.format(
            new_set = request.data['new_set'],
            old_set = request.data['old_set']
        )
        cursor = connection.cursor()
        cursor.execute(sql_product_set_update)

        return Response(format_body(1, 'Success', ''))


class ProductSetListView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_product_set_list

        if str(self.get.user_id).startswith('admin_'):
            owner = self.get.user_id
        else:
            owner = 'app_'+ self.get.user_id

        sql_product_set_list = sql_product_set_list.format(
            owner = owner,
            _image_prefix = image_path(),
            _limit = sql_limit(request)
        )
        cursor = connection.cursor()
        cursor.execute(sql_product_set_list)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'set_list': data}))


class ProductSetGoodsView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_product_set_goods

        if str(self.get.user_id).startswith('admin_'):
            owner = self.get.user_id
        else:
            owner = 'app_'+ self.get.user_id

        sql_product_set_goods = sql_product_set_goods.format(
            owner = owner,
            _image_prefix=image_path(),
            set = request.GET['set']
        )
        cursor = connection.cursor()
        cursor.execute(sql_product_set_goods)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'goods_list': data}))


class ImageUploadView(APIView):
    @raise_general_exception
    def post(self, request):
        image = request.FILES['image']
        sub_path = save_images(image, 'GoodsDetail')
        if image_path:
            url = image_path() + sub_path
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
            _image_prefix = image_path(),
            _keyword = request.GET['keyword'] if request.GET['keyword'] != 'all' else ''
        )

        cursor.execute(sql_product_search)

        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', data))


class GroupBuyingListView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_group_buying_list

        cursor = connection.cursor()

        sql_where = ""
        where_or_and = "WHERE "
        if request.GET['on_sale'] == '1':
            sql_where += "{} a.on_sale = {}".format(where_or_and, request.GET['on_sale'])
            where_or_and = " AND "
        if request.GET['ship_time']:
            sql_where += "{} a.ship_time >= '{}'".format(where_or_and, request.GET['ship_time'])
            where_or_and = " AND "
        if request.GET['title']:
            sql_where += "{} a.title LIKE '%{}%'".format(where_or_and, request.GET['title'])
            where_or_and = " AND "
        if request.GET['classify']:
            sql_where += "{} b.name LIKE '%{}%'".format(where_or_and, request.GET['classify'])

        _sql_group_buying_list = sql_group_buying_list.format(
            _where = sql_where,
            _order_by = 'ORDER BY a.id DESC ',
            _limit = sql_limit(request)
        )
        cursor.execute(_sql_group_buying_list)
        data = dict_fetch_all(cursor)

        _sql_goods_buying_list_count = sql_count(sql_group_buying_list.format(
            _where=sql_where,
            _order_by='',
            _limit=''
        ))
        cursor.execute(_sql_goods_buying_list_count)
        count = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {
            'groupbuying_list': data,
            'paged': {'total': count[0]['count']}
        }))


class GroupBuyingDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_group_buying_detail, sql_group_buying_products
        cursor = connection.cursor()

        sql_group_buying_detail = sql_group_buying_detail.format(id=request.GET['groupbuying_id'])
        sql_group_buying_products = sql_group_buying_products.format(
            image_prefix = image_path(),
            id = request.GET['groupbuying_id']
        )

        cursor.execute(sql_group_buying_detail)
        group_buying_detail = dict_fetch_all(cursor)[0]

        cursor.execute(sql_group_buying_products)
        group_buying_products = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'group_buying_detail': group_buying_detail, 'group_buying_products': group_buying_products}))


class GroupBuyingCreateView(APIView):
    @raise_general_exception
    def post(self, request):
        from market.models import GroupBuy
        from sqls import sql_group_buying_goods_create

        group_buying_info = request.data['groupbuying_info']
        group_buying_products = request.data['groupbuying_products']

        new_goupy_buying = GroupBuy(
            goods_classify_id = group_buying_info['classify'],
            title = group_buying_info['title'],
            end_time = group_buying_info['end_time'],
            ship_time = group_buying_info['ship_time'],
            add_time = datetime.now(),
            on_sale = group_buying_info['on_sale']
        )
        new_goupy_buying.save()

        insert_values = ""
        for product in group_buying_products:
            insert_values += "({price}, {stock}, '{unit}', {goods_id}, {group_buy_id}),".format(
                price = product['price'],
                stock = product['stock'],
                unit = product['unit'],
                goods_id = product['org_goods_id'],
                group_buy_id = new_goupy_buying.id
            )

        sql = sql_group_buying_goods_create % {'values': insert_values[0:-1]}

        cursor = connection.cursor()
        cursor.execute(sql)

        return Response(format_body(1, 'Success', ''))


class GroupBuyingUpdateView(APIView):
    @raise_general_exception
    def post(self, request):
        from market.models import GroupBuy
        from sqls import sql_group_buying_goods_update, sql_group_buying_goods_delete

        group_buying_info = request.data['groupbuying_info']
        group_buying_products = request.data['groupbuying_products']
        del_goods = request.data['del_goods']

        GroupBuy.objects.filter(pk=group_buying_info['id']).update(
            goods_classify_id = group_buying_info['classify'],
            title = group_buying_info['title'],
            end_time = group_buying_info['end_time'],
            ship_time = group_buying_info['ship_time'],
            add_time = datetime.now(),
            on_sale = group_buying_info['on_sale']
        )

        cursor = connection.cursor()

        if del_goods:
            sql = sql_group_buying_goods_delete.format(goods_id=','.join(del_goods))
            cursor.execute(sql)

        if group_buying_products:
            update_values = ""
            for product in group_buying_products:
                update_values += "({id}, {price}, {stock}, '{unit}', {goods_id}, {group_buy_id}),".format(
                    id = product['goods_id'],
                    price = product['price'],
                    stock = product['stock'],
                    unit = product['unit'],
                    goods_id = product['org_goods_id'],
                    group_buy_id = group_buying_info['id']
                )
            sql = sql_group_buying_goods_update % {'values': update_values[0:-1]}
            cursor.execute(sql)

        return Response(format_body(1, 'Success', ''))


class ClassifyListView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_classify_list
        cursor = connection.cursor()

        sql_classify_list = sql_classify_list.format(_image_prefix=image_path())
        cursor.execute(sql_classify_list)
        classify_list = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'classify_list': classify_list}))


class ClassifyUpdateView(APIView):
    @raise_general_exception
    def post(self, request):
        from sqls import sql_classify_list
        cursor = connection.cursor()

        classify = GoodsClassify.objects.get(pk=request.data['id'])
        classify.name = request.data['name']
        classify.desc = request.data['desc']

        if not request.data['icon']=='undefined':
            new_icon = save_images(request.data['icon'], 'Classify')
            classify.icon = new_icon
        if not request.data['image']=='undefined':
            new_image = save_images(request.data['image'], 'Classify')
            classify.image = new_image

        classify.save()

        cursor.execute(sql_classify_list.format(_image_prefix=image_path()))
        classify_list = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'classify_list': classify_list}))


class ClassifyCreateView(APIView):
    @raise_general_exception
    def post(self, request):
        from sqls import sql_classify_list
        cursor = connection.cursor()

        icon = save_images(request.data['icon'], 'Classify')
        image = save_images(request.data['icon'], 'Classify')

        classify = GoodsClassify(
            name=request.data['name'],
            desc=request.data['desc'],
            icon=icon,
            image=image
        )

        classify.save()

        cursor.execute(sql_classify_list.format(_image_prefix=image_path()))
        classify_list = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'classify_list': classify_list}))


class UserListView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_user_list
        cursor = connection.cursor()

        sql_where = ""
        where_or_and = "WHERE "
        if request.GET['nickname']:
            sql_where += "{} nickname LIKE '{}'".format(where_or_and, request.GET['nickname'])
            where_or_and = " AND "

        _sql_user_list = sql_user_list.format(**{
            '_where': sql_where,
            '_order_by': 'ORDER BY id DESC',
            '_limit': sql_limit(request)
        })
        _sql_user_list_count = sql_count(sql_user_list.format(**{
            '_where': sql_where,
            '_order_by': '',
            '_limit': ''
        }))

        cursor.execute(_sql_user_list)
        users = dict_fetch_all(cursor)

        cursor.execute(_sql_user_list_count)
        count = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'users': users, 'paged': {'total': count[0]['count']}}))


class UserProfileUpdateView(APIView):
    @raise_general_exception
    def post(self, request):
        user = UserProfile.objects.get(pk=request.data['user_id'])
        user.is_agent = request.data['role']
        user.save()

        return Response(format_body(1, 'Success', ''))


class GroupBuyingOrderView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_order_summary, sql_group_buying_sell_summary
        cursor = connection.cursor()

        sql_merchant_order_summary = sql_merchant_order_summary % ({'group_buy_id': request.GET['groupbuying_id']})
        cursor.execute(sql_merchant_order_summary)
        orders_summary = dict_fetch_all(cursor)
        for item in orders_summary:
            item['hgh'] = json.loads(item['hgh'])

        sql_group_buying_sell_summary = sql_group_buying_sell_summary.format(group_buy_id=request.GET['groupbuying_id'])
        cursor.execute(sql_group_buying_sell_summary)
        sell_summary = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'orders_summary': orders_summary, 'sell_summary': sell_summary}))


class MerchantOrderDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_merchant_order_detail
        cursor = connection.cursor()

        sql_merchant_order_detail = sql_merchant_order_detail.format(
            merchant_code=request.GET['merchant_code'],
            group_buying_id=request.GET['group_buying_id']
        )

        cursor.execute(sql_merchant_order_detail)
        order_detail = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', {'order_detail': order_detail}))








