# _*_ coding:utf-8 _*_
from django.conf.urls import url

from user import views as UserViews

urlpatterns = [
    url(r'consumer.order', UserViews.ConsumerOrderView.as_view(), name='consumer.order'),
    url(r'merchant.order', UserViews.MerchantOrderView.as_view(), name='merchant.order')
]