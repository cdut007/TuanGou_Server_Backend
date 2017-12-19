# _*_ coding:utf-8 _*_
from django.conf.urls import url

from user import views as UserViews
from shop import views as ShopViews
from other import views as OtherViews
from user import rp_views as RpViews

urlpatterns = [
    url(r'^user.login.app$', UserViews.UserLoginFromAppView.as_view(), name='user.login.app'),
    url(r'^user.login.web$', UserViews.UserLoginFromWebView.as_view(), name='user.login.web'),
    url(r'^user.info$', UserViews.UserInfoView.as_view(), name='user.info'),
    url(r'^merchant.info$', UserViews.MerchantInfoView.as_view(), name='merchant.info'),
    url(r'^user.sharing_code$', UserViews.UserSharingCodeView.as_view(), name='user.sharing_code'),
    # user -> web
    url(r'^consumer.order$', UserViews.ConsumerOrderView.as_view(), name='consumer.order'),
    url(r'^merchant.groupbuying.share$', UserViews.ShareGroupBuyingView.as_view(), name='merchant.groupbuying.share'),
    url(r'^merchant.jielong.cons$', UserViews.MerchantJieLongConsView.as_view(), name='merchnat.jielong.cons'),
    url(r'^consumer.order.list$', UserViews.GetConsumerOrderView.as_view(), name='consumer.order.list'),
    url(r'^consumer.order.detail$', UserViews.ConsumerOrderDetailView.as_view(), name='consumer.order.detail'),
    url(r'^consumer.order.ert$', UserViews.ConsumerOrderErtView.as_view(), name='consumer.order.ert'),
    # user -> app
    url(r'^merchant.order$', UserViews.MerchantOrderView.as_view(), name='merchant.order'),
    url(r'^merchant.group_buying.list$', UserViews.UserGroupBuyingView.as_view(), name='merchant.group_buying.list'),
    url(r'^merchant.notice.take_goods$', UserViews.MerchantNoticeConsumerTakeGoodsView.as_view(), name='merchant.notice.take_goods'),
    url(r'^merchant.mc.end$', UserViews.MerchantMcEnd.as_view(), name='merchant.mc.end'),
    url(r'^merchant.share.jielong$', UserViews.MerchantShareJieLong.as_view(), name='merchant.share.jielong'),
    url(r'^merchant.check.jielong.doing$', UserViews.MerchantCheckJieLongDoing.as_view(), name='merchant.check.jielong.doing'),
    url(r'^merchant.check.jielong.done$', UserViews.MerchantCheckJieLongDone.as_view(), name='merchant.check.jielong.done'),

    # shop -> web
    url(r'^merchant.index.page$', ShopViews.MerchantIndexPageView.as_view(), name='merchant.index.page'),
    url(r'^merchant.goods.detail$', ShopViews.MerchantGoodsDetailView.as_view(), name='merchant.goods.detail'),
    url(r'^merchant.goods.purchased.user$', ShopViews.MerchantGoodsPurchasedUserView.as_view(), name='goods.purchased.user'),
    url(r'^merchant.goods.list$', ShopViews.MerchantGoodsListView.as_view(), name='merchant.goods.list'),
    url(r'^merchant.classify.group_buy$', ShopViews.MerchantClassifyView.as_view(), name='merchant.classify.group_buy'),
    # shop -> app
    url(r'^goods.listing$', ShopViews.GoodsListingView.as_view(), name='goods.listing'),
    url(r'^goods.detail$', ShopViews.GoodsDetailView.as_view(), name='goods.detail'),
    url(r'^index.page$', ShopViews.IndexPageView.as_view(), name='index.page'),

    # other
    url(r'^winxin.js_sdk_config$', OtherViews.WeiXinJsSdkConfigView.as_view(), name='winxin.js_sdk_config'),
    url(r'^send.order.info$', OtherViews.SendOrderInfoView.as_view(), name='send.order.info'),
    url(r'^send.red.pack$', OtherViews.SendWxRedPacketView.as_view(), name='send.red.pack'),

    # red packets
    url(r'^rp.one.entries$', RpViews.RpOneEntriesView.as_view(), name='rp.one.entries'),
    url(r'^rp.unpack$', RpViews.UnpackRpView.as_view(), name='rp.unpack'),
]