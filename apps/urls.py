# _*_ coding:utf-8 _*_
from django.conf.urls import url

from user import views as UserViews


urlpatterns = [
    url(r'consumer.order', UserViews.GenericOrderView.as_view(), name='consumer.order')
]