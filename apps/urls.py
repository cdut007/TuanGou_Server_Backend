# _*_ coding:utf-8 _*_
from django.conf.urls import url

from user import views as UserViews
from shop import views as ShopViews

urlpatterns = [
    # user
    url(r'consumer.order', UserViews.ConsumerOrderView.as_view(), name='consumer.order'),
    url(r'merchant.order', UserViews.MerchantOrderView.as_view(), name='merchant.order'),

    # shop
    url(r'goods', ShopViews.GoodsView.as_view(), name='goods')
]