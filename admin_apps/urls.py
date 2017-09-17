# _*_ coding:utf-8 _*_
from django.conf.urls import url

import views


urlpatterns = [
    url(r'login', views.LogInView.as_view(), name='login'),
    url(r'product', views.ProductView.as_view(), name='product')
]