# _*_ coding:utf-8 _*_
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import UserDetail,Token

urlpatterns = [
    url(r'^user$', UserDetail.as_view(), name='user'),
    url(r'^token', Token.as_view(), name='token')
]

