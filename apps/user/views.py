# _*_ coding:utf-8 _*_
from datetime import datetime
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all
from ilinkgo.config import image_path
from market.models import GroupBuyGoods
from iuser.models import GenericOrder

from iuser.Authentication import Authentication


class GenericOrderView(APIView):
    @Authentication.token_required
    def get(self, request):
        from iuser.sql import sql_get_gengeric_order
        import json

        try:
            sql_get_shopping_cart = sql_get_gengeric_order % {
                'user_id': self.get.user_id,
                'agent_code': request.GET['agent_code'],
                'image_prefix': image_path(),
                'status_opt': '>=' if request.GET['status'] == '0' else '<='
            }
        except KeyError as e:
            return Response(format_body(2, 'Params error', e.message))

        cursor = connection.cursor()
        cursor.execute("SET SESSION group_concat_max_len = 204800;")
        cursor.execute(sql_get_shopping_cart)

        data = dict_fetch_all(cursor)

        for item in data:
            item['goods_list'] = json.loads(item['goods_list'])

        return Response(format_body(1, 'Success', {'group_buy': data}))


    @Authentication.token_required
    def post(self, request):
        from iuser.sql import sql_insert_generic_order

        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")

        # 插入订单
        insert_values = ""
        try:
            for goods_item in request.data['goods']:
                insert_values += "('{0}', '{1}', '{2}', '{3}', '{4}', {5}),\n".format(
                    request.data['agent_code'],
                    datetime.now(),
                    self.post.user_id,
                    goods_item['goods'],
                    goods_item['quantity'],
                    1
                )
            sql_insert_generic_order = sql_insert_generic_order % {'values': insert_values[0:-2]}
            cursor.execute(sql_insert_generic_order)

            group_buy_goods = GroupBuyGoods.objects.get(pk=request.data['goods'][0]['goods'])
        except KeyError as e:
            cursor.execute("ROLLBACK;")
            return Response(format_body(2, 'Params error', e.message))

        # 清空购物车
        try:
            if request.data['clear_cart'] is True:
                from iuser.sql import sql4
                goods_ids = ''
                for item in request.data['goods']:
                    goods_ids += str(item['goods']) + ','
                goods_ids = goods_ids.strip(',')
                sql4 = sql4 % {'user_id': self.post.user_id, 'agent_code': request.data['agent_code'], 'goods_ids': goods_ids}
                cursor.execute(sql4)
        except KeyError as e:
            cursor.execute("ROLLBACK;")
            return Response(format_body(2, 'Params error', e.message))

        #减少库存
        try:
            for item in request.data['goods']:
                sql_reduce_stock = "UPDATE market_groupbuygoods SET stock = stock - {0} WHERE id = {1};".format(item['quantity'], item['goods'])
                cursor.execute(sql_reduce_stock)
        except KeyError as e:
            cursor.execute("ROLLBACK;")
            return Response(format_body(2, 'Params error', e.message))

        cursor.execute("COMMIT;")

        return Response(format_body(1, 'Success', {'id': group_buy_goods.group_buy_id}))

    @Authentication.token_required
    def delete(self, request):
        # 删除订单
        try:
            order_goods = GenericOrder.objects.get(
                user=self.delete.user_id,
                agent_code=request.data['agent_code'],
                goods=request.data['goods_id']
            )
        except GenericOrder.DoesNotExist:
            return Response(format_body(0, 'order does not exist', ''))
        order_goods.status = 0
        order_goods.save()

        #更新库存
        order_goods.goods.stock += order_goods.quantity
        order_goods.goods.save()

        return Response(format_body(1, 'Success', ''))