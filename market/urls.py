# _*_ coding:utf-8 _*_
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from views import BannerList, GroupBuyList, HomePageList,GroupBuyGoodsDetail, GroupBuyDetailView, AgentHomePageList
from views import UploadImageVIew

urlpatterns = [
    # url(r'^', api_root, name='api_root'),
    url(r'^banner', BannerList.as_view(), name='banner'),
    url(r'^home_page_list', HomePageList.as_view(), name='home_page'),
    url(r'^agent_home_page_list', AgentHomePageList.as_view(), name='agent_home_page'),
    url(r'^group_buy_list', GroupBuyList.as_view(), name='group_buy_list'),
    url(r'^group_buy_detail', GroupBuyDetailView.as_view(), name='group_buy_detail'),
    url(r'^goods_detail', GroupBuyGoodsDetail.as_view(), name='goods_detail'),
    url(r'^upload_image', UploadImageVIew.as_view(), name='upload_image')
]
