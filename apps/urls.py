# _*_ coding:utf-8 _*_
from django.conf.urls import url

from user import views as UserViews
from shop import views as ShopViews
from other import views as OtherViews

urlpatterns = [
    # user
    url(r'consumer.order', UserViews.ConsumerOrderView.as_view(), name='consumer.order'),
    url(r'merchant.order', UserViews.MerchantOrderView.as_view(), name='merchant.order'),
    url(r'merchant.groupbuying.share', UserViews.ShareGroupBuyingView.as_view(), name='merchant.groupbuying.share'),

    # shop -> web
    url(r'merchant.goods.detail', ShopViews.MerchantGoodsDetailView.as_view(), name='merchant.goods.detail'),
    url(r'merchant.goods.purchased.user', ShopViews.MerchantGoodsPurchasedUserView.as_view(), name='goods.purchased.user'),
    url(r'merchant.goods.list', ShopViews.MerchantGoodsListView.as_view(), name='merchant.goods.list'),
    url(r'merchant.classify.group_buy', ShopViews.MerchantClassifyView.as_view(), name='merchant.classify.group_buy'),
    # shop -> app
    url(r'classify.group_buying', ShopViews.ClassifyView.as_view(), name='classify.group_buying'),

    # other
    url(r'winxin.js_sdk_config', OtherViews.WeiXinJsSdkConfigView.as_view(), name='winxin.js_sdk_config'),
]