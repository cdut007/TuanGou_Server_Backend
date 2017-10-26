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
from  MySQLdb import escape_string

from iuser.Authentication import Authentication


class ConsumerOrderView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_get_consumer_order

        sql_get_consumer_order = sql_get_consumer_order % {
            'consumer_id': self.get.user_id,
            'merchant_code': request.GET['merchant_code'],
            'image_prefix': image_path(),
            'group_buy_is_over': '>=' if request.GET['group_buy_is_over'] == '0' else '<='
        }

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_get_consumer_order)

        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        return Response(format_body(1, 'Success', {'group_buy': data}))

    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from sqls import sql_create_consumer_order, sql_done_consumer_order_update_stock, sql_create_consumer_order_remarks

        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")

        # 插入订单
        insert_values = ""
        for goods_item in request.data['goods_list']:
            insert_values += "('{0}', '{1}', '{2}', '{3}', '{4}', {5}),\n".format(
                request.data['merchant_code'],
                datetime.now(),
                self.post.user_id,
                goods_item['goods_id'],
                goods_item['goods_quantity'],
                1
            )
        sql_create_consumer_order = sql_create_consumer_order % {'values': insert_values[0:-2]}
        cursor.execute(sql_create_consumer_order)

        # 添加备注
        if request.data.has_key('remarks') and len(request.data['remarks']) > 0:
            insert_values = ""
            for remark in request.data['remarks']:
                insert_values += "('{group_buying_id}', '{user_id}', '{merchant_code}', '{remark}', '{add_time}'),\n".format(
                    group_buying_id = remark['group_buying_id'],
                    user_id = self.post.user_id,
                    merchant_code = request.data['merchant_code'],
                    remark = escape_string(remark['remark']),
                    add_time = datetime.now()
                )
            sql_create_consumer_order_remarks = sql_create_consumer_order_remarks % {'values': insert_values[0:-2]}
            cursor.execute(sql_create_consumer_order_remarks)

        # 清空购物车
        if request.data['clear_cart'] is True:
            from sqls import sql_clear_cart
            goods_ids = ''
            for item in request.data['goods_list']:
                goods_ids += str(item['goods_id']) + ','
            goods_ids = goods_ids.strip(',')
            sql_clear_cart = sql_clear_cart % {
                'consumer_id':  self.post.user_id,
                'merchant_code': request.data['merchant_code'],
                'goods_ids': goods_ids
            }
            cursor.execute(sql_clear_cart)

        #减少库存
        goods_id = 0
        try:
            for item in request.data['goods_list']:
                goods_id = item['goods_id']
                sql_reduce_stock = sql_done_consumer_order_update_stock.format(
                    item['goods_quantity'],
                    item['goods_id']
                )
                cursor.execute(sql_reduce_stock)
        except OperationalError as e:
            if e.args[0] == 1690:
                this_goods_current_stock = GroupBuyGoods.objects.get(pk=goods_id).stock
                return Response(format_body(12, 'Stock out of range', {'goods_id': goods_id, 'current_stock': this_goods_current_stock}))
            return Response(format_body(11, 'Mysql error', e.message))

        cursor.execute("COMMIT;")

        group_buy_goods = GroupBuyGoods.objects.get(pk=request.data['goods_list'][0]['goods_id'])

        return Response(format_body(1, 'Success', {'id': group_buy_goods.group_buy_id}))

    @raise_general_exception
    @Authentication.token_required
    def delete(self, request):
        # 删除订单
        order_goods = GenericOrder.objects.get(pk=request.GET['order_id'])
        order_goods.delete()

        #更新库存
        order_goods.goods.stock += order_goods.quantity
        order_goods.goods.save()

        return Response(format_body(1, 'Success', ''))


class MerchantOrderView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self,request):

        if request.GET['option'] == 'order_brief':
            return Response(format_body(1, 'Success', ''))

        elif request.GET['option'] == 'order_detail':
            from sqls import sql_merchant_order_detail

            sql_merchant_order_detail = sql_merchant_order_detail % {
                'merchant_code': request.GET['merchant_code'],
                'group_buy_id': request.GET['group_buy_id']
            }

            cursor = connection.cursor()
            cursor.execute("SET SESSION group_concat_max_len = 204800;")
            cursor.execute(sql_merchant_order_detail)
            data = dict_fetch_all(cursor)

            for item in data:
                item['goods_list'] = json.loads(item['goods_list'])

            return Response(format_body(1, 'Success', {'order_detail': data}))

        else:
            return Response(format_body(13, 'No this option', ''))


class ShareGroupBuyingView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def get(self, request):
        from sqls import sql_share_latest_groupbuying

        sql_share_latest_groupbuying = sql_share_latest_groupbuying.format(
            image_prefix=image_path(),
            user_id=self.get.user_id
        )

        cursor = connection.cursor()
        cursor.execute(sql_share_latest_groupbuying)
        data = dict_fetch_all(cursor)

        return Response(format_body(1, 'success', data))



