# _*_ coding:utf-8 _*_
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from views import BannerList, GroupBuyList, HomePageList,GroupBuyGoodsDetail, GoodsList

urlpatterns = format_suffix_patterns([
    # url(r'^', api_root, name='api_root'),
    url(r'^banner', BannerList.as_view(), name='banner'),
    url(r'^home_page_list', HomePageList.as_view(), name='home_page'),
    url(r'^group_buy_list/(?P<pk>[0-9]+)$', GroupBuyList.as_view(), name='group_buy_list'),
    url(r'^group_buy_detail/(?P<pk>[0-9]+)$', GoodsList.as_view(), name='group_buy_detail'),
    url(r'^goods_detail/(?P<pk>[0-9]+)$', GroupBuyGoodsDetail.as_view(), name='goods_detail')
])
