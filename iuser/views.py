from datetime import datetime
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from utils.common import format_body
from ilinkgo.config import web_link
from utils.winxin import code_to_access_token, access_token_to_user_info
from market.models import GroupBuyGoods, GroupBuy, GoodsClassify
from market.serializers import GroupBuyGoodsSerializer, GoodsClassifySerializer, GroupBuySerializer
from models import UserProfile, AgentOrder, ShoppingCart, GenericOrder
from serializers import UserProfileSerializer, UserAddressSerializer, AgentOrderSerializer, AgentApplySerializer, \
    ShoppingCartSerializer, GenericOrderSerializer, GenericOrderSerializer2

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
        return Response(format_body(1, 'Success', {'user_profile': serializer.data}))

    def post(self, request, format=None):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_record = UserProfile.objects.filter(unionid=serializer.validated_data['unionid']).first()
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
        data = code_to_access_token(code)
        try:
            user_info = access_token_to_user_info(data['access_token'], data['openid'])
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
                generic_orders = GenericOrder.objects.filter(agent_code=self.get.user_id, goods=single_goods['id'])
                single_goods['purchased'] =  generic_orders.aggregate(Sum('quantity'))['quantity__sum'] if generic_orders.aggregate(Sum('quantity'))['quantity__sum'] else 0
            agent_order['classify'] = GoodsClassifySerializer(group_buy.goods_classify).data
            agent_order['group_buy'] =GroupBuySerializer(group_buy).data
            agent_order['goods'] = goods_serializer.data

        return Response(format_body(1, 'Success', {'order': orders_serializer.data}))

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
            if order_record:
                return Response(format_body(4, 'The user already applied this group_buy', ''))
            serializer.save()
            return Response(format_body(1, 'Success', {'agent_url': web_link() + '?agent_code=' + user.openid}))
        return Response(format_body(2, serializer.errors, ''))


class ShoppingCartView(APIView):
    @Authentication.token_required
    def get(self, request):
        agent_code = request.GET.get('agent_code', '')
        group_buys = GroupBuy.objects.filter(
            group_buy_goods__shoppingcart__user=self.get.user_id,
            group_buy_goods__shoppingcart__agent_code=agent_code
        ).distinct()

        group_buys_serializer = GroupBuySerializer(group_buys, many=True)
        for group_buy in group_buys_serializer.data:
            classify_serializer = GoodsClassifySerializer(GoodsClassify.objects.get(group_buy=group_buy['id']))
            group_buy['classify'] = classify_serializer.data
            cart_goods = ShoppingCart.objects.filter(user=self.get.user_id, agent_code=agent_code, goods__group_buy=group_buy['id'])
            cart_goods_serializer = ShoppingCartSerializer(cart_goods, many=True)
            for item in cart_goods_serializer.data:
                goods_info = GroupBuyGoodsSerializer(GroupBuyGoods.objects.get(pk=item['goods']))
                item['goods'] = goods_info.data
            group_buy['cart_goods'] = cart_goods_serializer.data
        return Response(format_body(1, 'Success', {'group_buy': group_buys_serializer.data}))

    @Authentication.token_required
    def post(self, request):
        request.data['user'] = self.post.user_id
        serializer = ShoppingCartSerializer(data=request.data)
        if serializer.is_valid():
            record = ShoppingCart.objects.filter(
                user=self.post.user_id,
                agent_code=request.data['agent_code'],
                goods=request.data['goods']).first()
            if record:
                record.quantity += request.data['quantity']
                record.save()
            else:
                serializer.save()
            return Response(format_body(1, 'Success', ''))
        return Response(format_body(2, serializer.errors, ''))

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
        try:
            cart = ShoppingCart.objects.get(pk=request.data['cart_id'])
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
        for group_buy in group_buys_serializer.data:
            classify_serializer = GoodsClassifySerializer(GoodsClassify.objects.get(group_buy=group_buy['id']))
            group_buy['classify'] = classify_serializer.data
            goods = GenericOrder.objects.filter(user=self.get.user_id, agent_code=agent_code, goods__group_buy=group_buy['id'])
            goods_serializer = GenericOrderSerializer2(goods, many=True)
            for item in goods_serializer.data:
                goods_info = GroupBuyGoodsSerializer(GroupBuyGoods.objects.get(pk=item['goods']))
                item['goods'] = goods_info.data
            group_buy['order_goods'] = goods_serializer.data
        return Response(format_body(1, 'Success', {'group_buy': group_buys_serializer.data}))

    @Authentication.token_required
    def post(self, request):
        request.data['user'] = self.post.user_id
        order_serializer = GenericOrderSerializer(data=request.data)
        if not order_serializer.is_valid():
            return Response(format_body(2, order_serializer.errors, ''))
        order_bulk = []
        for item in order_serializer.data['goods']:
            order_record = GenericOrder.objects.filter(
                user=self.post.user_id,
                agent_code=request.data['agent_code'],
                goods=item['goods']
            ).first()
            if order_record:
                order_record.quantity += item['quantity']
                order_record.save()
                continue
            order_bulk.append(GenericOrder(
               user=order_serializer.validated_data['user'],
               agent_code=order_serializer.validated_data['agent_code'],
               goods = GroupBuyGoods.objects.get(pk=item['goods']),
               quantity=item['quantity']
            ))
        GenericOrder.objects.bulk_create(order_bulk)
        return Response(format_body(1, 'Success', ''))

