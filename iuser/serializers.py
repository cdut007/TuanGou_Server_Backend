# _*_ coding: utf-8 _*_
from  rest_framework import serializers

from  models import UserProfile, AgentOrder, AgentApply, ShoppingCart, GenericOrder
from market.serializers import GroupBuyGoodsSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    privilege = serializers.ListField()
    class Meta:
        model = UserProfile
        fields = ('id','nickname', 'openid', 'sex', 'province', 'city', 'country', 'headimgurl', 'privilege', 'unionid')


class UserAddressSerializer(serializers.ModelSerializer):
    phone_num = serializers.CharField(required=True)
    address = serializers.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ( 'phone_num', 'address')


class AgentApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentApply
        fields = ('name', 'user')


class AgentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentOrder
        fields = ('id', 'group_buy', 'user', 'goods_ids')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'goods', 'quantity','agent_code')

    def to_representation(self, instance):
        data = super(ShoppingCartSerializer, self).to_representation(instance)
        data['cart_id'] = data['id']
        data.pop('id')
        data.pop('agent_code')
        data.pop('user')
        return data


class GenericOrderSerializer(serializers.ModelSerializer):
    goods = serializers.ListField(child=serializers.JSONField())
    class Meta:
        model = GenericOrder
        fields = ('id', 'user','agent_code', 'goods', 'quantity')


class GenericOrderSerializer2(serializers.ModelSerializer):
    class Meta:
        model = GenericOrder
        fields = ('id', 'user','agent_code', 'goods', 'quantity')

    def to_representation(self, instance):
        data = super(GenericOrderSerializer2, self).to_representation(instance)
        data.pop('agent_code')
        data.pop('user')
        return data