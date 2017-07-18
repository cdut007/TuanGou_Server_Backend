# _*_ coding:utf-8 _*_
from django.conf.urls import url

from views import UserView, UserAddressView, AgentOrderView, AgentApplyView, ShoppingCartView, GenericOrderView
from views import WebUserView, AgentInfoView
urlpatterns = [
    url(r'^user$', UserView.as_view(), name='user'),
    url(r'^agent_info', AgentInfoView.as_view(), name='agent_view'),
    url(r'^web_user', WebUserView.as_view(), name='web_user'),
    url(r'user_address', UserAddressView.as_view(), name='user_address'),
    url(r'agent_order', AgentOrderView.as_view(), name='agent_order'),
    url(r'agent_apply', AgentApplyView.as_view(), name='agent_apply'),
    url(r'shopping_cart', ShoppingCartView.as_view(), name='shopping_cart'),
    url(r'generic_order', GenericOrderView.as_view(), name='generic_order')
]

