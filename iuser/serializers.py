# _*_ coding: utf-8 _*_
from  rest_framework import serializers

from  models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id','nickname', 'openid', 'sex', 'province', 'city', 'country', 'headimgurl', 'privilege', 'unionid')