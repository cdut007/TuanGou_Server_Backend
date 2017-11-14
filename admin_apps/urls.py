# _*_ coding:utf-8 _*_
from django.conf.urls import url

import views


urlpatterns = [
    url(r'login', views.LogInView.as_view(), name='login'),
    url(r'goods.list$', views.ProductListView.as_view(), name='product.list'),
    url(r'goods.list.set', views.ProductSetGoodsView.as_view(), name='product.list.set'),
    url(r'goods.set$', views.ProductSetListView.as_view(), name='product.set'),
    url(r'goods.detail', views.ProductDetailView.as_view(), name='product.detail'),
    url(r'goods.create', views.ProductCreateView.as_view(), name='product.create'),
    url(r'goods.update', views.ProductUpdateView.as_view(), name='product.update'),
    url(r'goods.set.update', views.ProductSetUpdateView.as_view(), name='product.set.update'),
    url(r'image.upload', views.ImageUploadView.as_view(), name='image.upload'),
    url(r'image.clean', views.CleanImages.as_view(), name='image.clean'),
    url(r'goods.search', views.ProductSearchView.as_view(), name='goods.search'),
    url(r'classify.list', views.ClassifyListView.as_view(), name='classify.list'),
    url(r'classify.create', views.ClassifyCreateView.as_view(), name='classify.create'),
    url(r'classify.update', views.ClassifyUpdateView.as_view(), name='classify.update'),
    url(r'groupbuying.list', views.GroupBuyingListView.as_view(), name='groupbuying.list'),
    url(r'groupbuying.detail', views.GroupBuyingDetailView.as_view(), name='groupbuying.detail'),
    url(r'groupbuying.create', views.GroupBuyingCreateView.as_view(), name='groupbuying.create'),
    url(r'groupbuying.update', views.GroupBuyingUpdateView.as_view(), name='groupbuying.update'),
    url(r'groupbuying.order.summary', views.GroupBuyingOrderView.as_view(), name='groupbuying.order.summary'),
    url(r'groupbuying.order.detail', views.MerchantOrderDetailView.as_view(), name='groupbuying.order.detail'),
    url(r'user.list', views.UserListView.as_view(), name='user.list'),
    url(r'user.update', views.UserProfileUpdateView.as_view(), name='user.update')
]