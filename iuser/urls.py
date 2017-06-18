# _*_ coding:utf-8 _*_
from django.conf.urls import url

from views import UserView, UserAddressView, AgentOrderView

urlpatterns = [
    url(r'^user$', UserView.as_view(), name='user'),
    url(r'user_address', UserAddressView.as_view(), name='user_address'),
    url(r'agent_order', AgentOrderView.as_view(), name='agent_order')
]

