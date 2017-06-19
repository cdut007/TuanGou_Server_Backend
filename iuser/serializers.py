# _*_ coding: utf-8 _*_
from  rest_framework import serializers

from  models import UserProfile, AgentOrder, AgentApply


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