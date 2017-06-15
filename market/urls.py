# _*_ coding:utf-8 _*_
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from views import BannerList, GoodsClassifyList, GroupBuyList, HomePage

urlpatterns = format_suffix_patterns([
    # url(r'^', api_root, name='api_root'),
    url(r'^banner/$', BannerList.as_view(), name='banner'),
    url(r'^classify/$', GoodsClassifyList.as_view(), name='classify'),
    url(r'^group_buy/', GroupBuyList.as_view(), name='group_buy'),
    url(r'^home_page_list/', HomePage.as_view(), name='home_page')
])
