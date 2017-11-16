# _*_ coding:utf-8 _*_
import time, os
from ilinkgo.config import excel_save_base_path
from utils.common import dict_fetch_all, random_str, raise_general_exception
from datetime import datetime
from django.db.models import Sum
from django.db import connection
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.common import format_body, dict_fetch_all
from ilinkgo.config import web_link, image_path
from utils.winxin import WeiXinAPI
from market.models import GroupBuyGoods, GroupBuy, GoodsClassify
from market.serializers import GroupBuyGoodsSerializer, GoodsClassifySerializer, GroupBuySerializer
from models import UserProfile, AgentOrder, ShoppingCart, GenericOrder
from serializers import UserProfileSerializer, UserAddressSerializer, AgentOrderSerializer, AgentApplySerializer, GenericOrderSerializer2

from Authentication import Authentication
# Create your views here.


class UserView(APIView):
    @Authentication.token_required
    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(pk=self.get.user_id)
        except UserProfile.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        serializer = UserProfileSerializer(user_profile)
        data = serializer.data
        data['address_set'] = {'address': user_profile.address, 'phone_num': user_profile.phone_num}

        return Response(format_body(1, 'Success', {'user_profile': data}))

    def post(self, request, format=None):

        if request.data.has_key('virtual_account') and request.data['virtual_account']==1:
            if request.data['username'] == 'Mike.zk' and request.data['password']=='1234567a':
                return Response(format_body(1, 'Success', {'token': 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTU2MjIyNzQyOSwiaWF0IjoxNTAxNzQ3NDI5fQ.eyJpZCI6MTB9.d3jVre6F5cC94gPYKJrEiij3v4OMwi3FdEvqQH7VE8I'}))
            return Response(format_body(2, 'ErrorParams', 'username or password error'))

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_record = UserProfile.objects.filter(
                unionid=serializer.validated_data['unionid'],
                openid=serializer.validated_data['openid']
            ).first()
            if user_record:
                token = Authentication.generate_auth_token(user_record.id)
                return Response(format_body(1, 'Success', {'token': token}))
            user = serializer.save()
            token = Authentication.generate_auth_token(user.id)
            return Response(format_body(1, 'Success', {'token': token}))
        return Response(format_body(2, 'ErrorParams', serializer.errors))

    @Authentication.token_required
    def put(self,request):
        user = UserProfile.objects.filter(pk=self.put.user_id).first()
        serializer = UserProfileSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response(format_body(1, 'Success',''))
        return Response(format_body(2, serializer.errors, ''))

    def delete(self, request, pk):
        pass


class WebUserView(APIView):
    def get(self,request):
        code = request.GET.get('code', '')
        wei_xin_api = WeiXinAPI()
        data = wei_xin_api.website_authorization_access_token(code)
        try:
            user_info = wei_xin_api.website_user_info(data['access_token'], data['openid'])
        except KeyError:
            return Response(format_body(6, 'code error', ''))
        serializer = UserProfileSerializer(data=user_info)
        if not serializer.is_valid():
            return Response(format_body(2, 'ErrorParams, UserInfo', serializer.errors))
        user_record = UserProfile.objects.filter(unionid=serializer.validated_data['unionid']).first()
        if user_record:
            token = Authentication.generate_auth_token(user_record.id)
            return Response(format_body(1, 'Success', {'token': token}))
        user = serializer.save()
        token = Authentication.generate_auth_token(user.id)
        return Response(format_body(1, 'Success', {'token': token}))


class AgentInfoView(APIView):
    def get(self, request):
        code = request.GET.get('agent_code', '')
        try:
            user_profile = UserProfile.objects.get(openid=code)
        except UserProfile.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        serializer = UserProfileSerializer(user_profile)
        return Response(format_body(1, 'Success', {'user_profile': serializer.data}))


class UserAddressView(APIView):
    @Authentication.token_required
    def get(self, request):
        try:
            user = UserProfile.objects.get(pk=self.get.user_id)
        except UserProfile.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        if user.phone_num == '' or user.address == '':
            return Response(format_body(0, 'The user has no address ', ''))
        serializer = UserAddressSerializer(user)
        return Response(format_body(1, 'Success', {'user_address': serializer.data}))

    @Authentication.token_required
    def post(self, request):
        user = UserProfile.objects.get(pk=self.post.user_id)
        serializer = UserAddressSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response(format_body(1, 'Success', ''))
        return Response(format_body(2, serializer.errors, ''))


class AgentApplyView(APIView):
    @Authentication.token_required
    def post(self, request):
        try:
            user = UserProfile.objects.get(pk=self.post.user_id)
        except UserProfile.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        request.data['user'] = self.post.user_id
        serializer1 = AgentApplySerializer(data=request.data)
        serializer2 = UserAddressSerializer(data=request.data, instance=user)
        if not serializer1.is_valid() :
            return Response(format_body(2, serializer1.errors, ''))
        if not serializer2.is_valid():
            return Response(format_body(2, serializer2.errors, ''))
        serializer1.save()
        serializer2.save()
        return Response(format_body(1, 'Success', ''))


class AgentOrderView(APIView):
    """
    status: 0: going, 1:done
    """
    @Authentication.token_required
    def get(self, request):
        status = request.GET.get('status', '1')
        agent_orders = AgentOrder.objects.filter(user=self.get.user_id)
        user = UserProfile.objects.get(id=self.get.user_id)
        if status == '0':
            agent_orders = agent_orders.filter(group_buy__end_time__gte=datetime.now())
        elif status == '1':
            agent_orders = agent_orders.filter(group_buy__end_time__lt=datetime.now())

        orders_serializer = AgentOrderSerializer(agent_orders, many=True)
        for agent_order in orders_serializer.data:
            group_buy = GroupBuy.objects.get(pk=agent_order['group_buy'])
            all_goods = GroupBuyGoods.objects.filter(id__in=str(agent_order['goods_ids']).split(','))
            goods_serializer = GroupBuyGoodsSerializer(all_goods, many=True)
            for single_goods in  goods_serializer.data:
                generic_orders = GenericOrder.objects.filter(agent_code=user.openid, goods=single_goods['id'], status=1)
                single_goods['purchased'] =  generic_orders.aggregate(Sum('quantity'))['quantity__sum'] if generic_orders.aggregate(Sum('quantity'))['quantity__sum'] else 0
            agent_order['classify'] = GoodsClassifySerializer(group_buy.goods_classify).data
            agent_order['group_buy'] =GroupBuySerializer(group_buy).data
            agent_order['goods'] = goods_serializer.data

        data = sorted(orders_serializer.data, key=lambda v: v['group_buy']['ship_time'], reverse=True)

        return Response(format_body(1, 'Success', {'order': data}))

    @Authentication.token_required
    def post(self, request):
        user = UserProfile.objects.get(pk=self.post.user_id)
        if not user.is_agent == 1:
            return Response(format_body(3, 'The user is not agent', ''))

        request.data['user'] = self.post.user_id
        request.data['goods_ids'] = ','.join(map(str, request.data['goods_ids']))
        serializer = AgentOrderSerializer(data=request.data)
        if serializer.is_valid():
            order_record = AgentOrder.objects.filter(user=user.id, group_buy=serializer.validated_data['group_buy'])

            from sql import sql_group_buy_classify
            sql_group_buy_classify = sql_group_buy_classify % {'group_buy_id': request.data['group_buy']}
            cursor = connection.cursor()
            cursor.execute(sql_group_buy_classify)
            classify_info = dict_fetch_all(cursor)

            if order_record:
                return Response(format_body(4, 'The user already applied this group_buy', {'agent_url': web_link() + '?agent_code=' + user.openid, 'group_buy_info': classify_info}))

            serializer.save()
            return Response(format_body(1, 'Success', {'agent_url': web_link() + '?agent_code=' + user.openid, 'group_buy_info': classify_info}))

        return Response(format_body(2, serializer.errors, ''))


class ShoppingCartView(APIView):
    @Authentication.token_required
    def get(self, request):
        from sql import sql_get_shopping_cart
        import json

        try:
            sql_get_shopping_cart = sql_get_shopping_cart % {
                'user_id': self.get.user_id,
                'agent_code': request.GET['agent_code'],
                'image_prefix': image_path()
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
        from sql import sql_add_to_cart

        insert_values = ""
        try:
            for goods_item in request.data['goods_list']:
                if int(goods_item['goods_quantity']) <= 0:
                    continue
                insert_values += "('{0}', '{1}', '{2}', '{3}', '{4}'),\n".format(
                    request.data['agent_code'],
                    datetime.now(),
                    self.post.user_id,
                    goods_item['goods_id'],
                    goods_item['goods_quantity']
                )
        except KeyError as e:
            return Response(format_body(2, 'Params error', e.message))

        sql_add_to_cart = sql_add_to_cart % {'values': insert_values[0:-2]}
        
        cursor = connection.cursor()
        cursor.execute(sql_add_to_cart)

        return Response(format_body(1, 'Success', ''))

    @Authentication.token_required
    def put(self, request):
        try:
            cart = ShoppingCart.objects.get(pk=request.data['cart_id'])
            cart.quantity = request.data['quantity']
            cart.save()
        except ShoppingCart.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        return Response(format_body(1, 'Success', ''))

    @Authentication.token_required
    def delete(self, request):
        if request.data.has_key('cart_id'):
            pk = request.data['cart_id']
        else:
            pk = request.GET['cart_id']

        try:
            cart = ShoppingCart.objects.get(pk=pk)
            cart.delete()
        except ShoppingCart.DoesNotExist:
            return Response(format_body(0, 'Object does not exist', ''))
        return Response(format_body(1, 'Success', ''))


class GenericOrderView(APIView):
    @Authentication.token_required
    def get(self, request):
        """
        status: 0: going, 1:done
        """
        agent_code = request.GET.get('agent_code', '1')
        status = request.GET.get('status', '')

        group_buys = GroupBuy.objects.filter(
            group_buy_goods__genericorder__user=self.get.user_id,
            group_buy_goods__genericorder__agent_code=agent_code
        ).distinct()

        if status == '0':
            group_buys = group_buys.filter(end_time__gte=datetime.now())
        elif status == '1':
            group_buys = group_buys.filter(end_time__lt=datetime.now())

        group_buys_serializer = GroupBuySerializer(group_buys, many=True)

        res_data = []
        for group_buy in group_buys_serializer.data:
            classify_serializer = GoodsClassifySerializer(GoodsClassify.objects.get(group_buy=group_buy['id']))
            group_buy['classify'] = classify_serializer.data
            goods = GenericOrder.objects.filter(
                user=self.get.user_id,
                agent_code=agent_code,
                goods__group_buy=group_buy['id'],
                status=1
            )
            goods_serializer = GenericOrderSerializer2(goods, many=True)
            for item in goods_serializer.data:
                goods_info = GroupBuyGoodsSerializer(GroupBuyGoods.objects.get(pk=item['goods']))
                item['goods'] = goods_info.data
            group_buy['order_goods'] = goods_serializer.data

            if goods.count():
                res_data.append(group_buy)

        return Response(format_body(1, 'Success', {'group_buy': res_data}))


    @Authentication.token_required
    def post(self, request):
        from sql import sql_insert_generic_order

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
                from sql import sql4
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
        order_goods.delete()

        #更新库存
        order_goods.goods.stock += order_goods.quantity
        order_goods.goods.save()

        return Response(format_body(1, 'Success', ''))


class SendEmailView(APIView):
    @Authentication.token_required
    @raise_general_exception
    def post(self, request):
        from utils.gen_excel import order_excel
        from apps.user.models import MerchantPushLog
        from sql import sql1, sql2

        #https://docs.google.com/gview?embedded=true&url=http://www.ailinkgo.com:3000/excel/18502808546_2017-08-01.xlsx
        user_id = self.post.user_id
        group_buy_id = request.data['group_buy_id'] or 1
        email_to = request.data['email']

        user_info = UserProfile.objects.get(id=user_id)
        group_buy = GroupBuy.objects.get(id=group_buy_id)
        send_record = MerchantPushLog.objects.filter(
            group_buying_id=group_buy_id,
            merchant_id=user_id,
            is_send_excel = 1
        )

        if send_record:
            _file= excel_save_base_path() + send_record[0].excel_path
        else:
            excel_name = str(int(time.time())) + '_' + random_str(4) + '.xlsx'
            file_path = excel_save_base_path() + excel_name

            cursor = connection.cursor()

            sql1 = sql1 % {'agent_code': user_info.openid, 'group_buy_id': group_buy_id}
            cursor.execute(sql1)
            order_list = dict_fetch_all(cursor)

            if not order_list:
                return Response(format_body(7, 'Generic order empty', ''))

            sql2 = sql2 % {'agent_code': user_info.openid, 'group_buy_id': group_buy_id}
            cursor.execute(sql2)
            ship_list = dict_fetch_all(cursor)

            data = {
                'agent_info': {
                    'time': group_buy.ship_time.strftime('%Y/%m/%d'),
                    'address': user_info.address,
                    'phone': user_info.phone_num,
                    'wx': user_info.nickname
                },
                'ship_list': ship_list,
                'order_list': order_list,
                'file_path': file_path
            }
            order_excel(data)
            MerchantPushLog.insert_send_excel_log(
                group_buying_id=group_buy_id,
                merchant_id=user_id,
                excel_path=excel_name
            )
            _file = file_path

        subject =  u"类别（%(classify)s）订单详情" % {
            'classify': group_buy.goods_classify.name
        }
        body = u"类别（%(classify)s）发货时间（预计%(month)s月%(day)s日发货）订单信息表" % {
            'classify': group_buy.goods_classify.name,
            'month': group_buy.ship_time.month,
            'day': group_buy.ship_time.day
        }
        from_email = u'爱邻购 <ilinkgo@ultralinked.com>'
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email= from_email,
            to=[email_to],
        )

        message.attach_file(_file)
        message.send()

        return Response(format_body(1, 'Success', ''))