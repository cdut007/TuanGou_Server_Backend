# _*_ coding:utf-8 _*_
import json
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from ilinkgo.settings import conf
from utils.common import format_body, dict_fetch_all, raise_general_exception, sql_limit

from iuser.Authentication import Authentication
from iuser.models import AgentOrder, UserProfile


class MerchantGoodsDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_goods_detail, sql_merchant_goods_detail_related, sql_goods_classify
        from sqls import sql_goods_purchased_user

        query = {
            'goods_id': request.GET['goods_id'],
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': conf.image_url_prefix,
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
            _limit='LIMIT 0, 5'
        )

        cursor.execute(sql_goods_purchased_user)
        purchased_user = dict_fetch_all(cursor)

        def pop_count(v):
            v.pop('count')
            return v

        goods_detail['purchased_user'] = {
            'users': map(pop_count, purchased_user[:-1]),
            'count': purchased_user[-1]['count']
        }

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

        def pop_count(v):
            v.pop('count')
            return v

        return Response(format_body(1, 'Success', {'purchased_user': map(pop_count, purchased_user[:-1])}))


class MerchantGoodsListView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_goods_list

        sql_goods_detail = sql_goods_list.format(**{
            'group_buy_id': request.GET['group_buy_id'],
            'image_prefix': conf.image_url_prefix
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
        from sqls import sql_merchant_classify_group_buying_list, sql_merchant_group_buying_goods_list

        merchant = UserProfile.objects.get(merchant_code=request.GET['merchant_code'])
        classify_id = request.GET['classify_id']

        cursor.execute("SET SESSION group_concat_max_len = 20480;")
        cursor.execute(sql_classify_info.format(
            image_prefix = conf.image_url_prefix,
            classify_id = classify_id
        ))
        classify_info = dict_fetch_all(cursor)
        classify_info = classify_info[0]

        cursor.execute(sql_merchant_classify_group_buying_list.format(
            _merchant_id = merchant.id,
            _classify_id = classify_id
        ))
        group_buying_list = dict_fetch_all(cursor)

        def recombine_goods_list(v):
            if v['purchased_user']:
                _purchased_user = json.loads(v['purchased_user'])
            else:
                _purchased_user = []
            v['purchased_user'] = {
                'users': _purchased_user,
                'count': v['purchased_user_count']
            }
            v.pop('purchased_user_count')
            return v

        for group_buying in  group_buying_list:
            ao = AgentOrder.objects.get(
                group_buy_id = group_buying['group_buy_id'],
                user_id = merchant.id
            )
            sql_goods_list = sql_merchant_group_buying_goods_list % {
                'goods_ids': ao.goods_ids,
                'image_prefix': conf.image_url_prefix
            }
            cursor.execute(sql_goods_list)
            goods_list = dict_fetch_all(cursor)
            group_buying['goods_list'] = map(recombine_goods_list, goods_list)

        data = {
            'classify': classify_info,
            'group_buy_list': group_buying_list
        }

        return Response(format_body(1, 'Success', data))


class GoodsListingView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_classify_info
        from sqls import sql_classify_group_buy_list_with_all_goods

        query = {
            'classify_id': request.GET['classify_id'],
            'image_prefix': conf.image_url_prefix,
        }

        sql_classify_info = sql_classify_info.format(**query)
        sql_classify_group_buy_list = sql_classify_group_buy_list_with_all_goods % query

        cursor.execute(sql_classify_info)
        info = dict_fetch_all(cursor)[0]

        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_classify_group_buy_list)
        group_buying_list = dict_fetch_all(cursor)

        for item in group_buying_list:
            item['goods_list'] = json.loads(item['goods_list'])

        data = {
            'classify': info,
            'group_buying_list': group_buying_list,
        }

        return Response(format_body(1, 'Success', data))


class GoodsDetailView(APIView):
    @raise_general_exception
    def get(self, request):
        cursor = connection.cursor()

        from sqls import sql_goods_detail_app, sql_goods_related_app, sql_goods_classify

        query = {
            'goods_id': request.GET['goods_id'],
            'image_prefix': conf.image_url_prefix,
        }

        sql_goods_detail = sql_goods_detail_app.format(**query)
        sql_goods_related = sql_goods_related_app.format(**query)
        sql_goods_classify = sql_goods_classify.format(**query)

        cursor.execute(sql_goods_detail)
        goods_detail = dict_fetch_all(cursor)[0]
        goods_detail['images'] = json.loads(goods_detail['images'])

        cursor.execute(sql_goods_classify)
        classify = dict_fetch_all(cursor)[0]

        cursor.execute(sql_goods_related)
        related_goods = dict_fetch_all(cursor)

        data = {
            'goods_detail': goods_detail,
            'related_goods': related_goods,
            'classify': classify
        }

        return Response(format_body(1, 'Success', data))


class IndexPageView(APIView):
    @raise_general_exception
    def get(self, request):
        from sqls import sql_app_index_page
        cursor = connection.cursor()

        cursor.execute(sql_app_index_page.format(image_prefix=conf.image_url_prefix))
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', data))


class MerchantIndexPageView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_web_index_page
        cursor = connection.cursor()

        cursor.execute(sql_web_index_page.format(
            image_prefix = conf.image_url_prefix,
            user_id = self.get.user_id
        ))
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'Success', data))



