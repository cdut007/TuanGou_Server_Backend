# _*_ coding:utf-8 _*_
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from views import BannerList, GoodsClassifyList, GroupBuyList, HomePageList,GroupBuyGoodsDetail

urlpatterns = format_suffix_patterns([
    # url(r'^', api_root, name='api_root'),
    url(r'^banner/$', BannerList.as_view(), name='banner'),
    url(r'^home_page_list/', HomePageList.as_view(), name='home_page'),
    url(r'^goods_detail/(?P<pk>[0-9]+)$', GroupBuyGoodsDetail.as_view(), name='goods_detail')
])
