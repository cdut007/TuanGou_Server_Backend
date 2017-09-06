# _*_ coding:utf-8 _*_
from django.conf.urls import url
from admin_views import GroupBuyAdminView

urlpatterns = [
    url(r'^group_buy', GroupBuyAdminView.as_view(), name='group_buy_admin'),
]
