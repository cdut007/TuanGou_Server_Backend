# _*_ coding:utf-8 _*_
from django.conf.urls import url

import views


urlpatterns = [
    url(r'login', views.LogInView.as_view(), name='login'),
    url(r'goods.list', views.ProductListView.as_view(), name='product.list'),
    url(r'goods.detail', views.ProductDetailView.as_view(), name='product.detail'),
    url(r'goods.create', views.ProductCreateView.as_view(), name='product.create'),
    url(r'image.upload', views.ImageUploadView.as_view(), name='image.upload')
]