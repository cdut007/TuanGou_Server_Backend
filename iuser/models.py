# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models

from market.models import GroupBuy, GroupBuyGoods

# Create your models here.

class UserProfile(models.Model):
    nickname = models.CharField(max_length=64, verbose_name=u'昵称')
    openid = models.CharField(max_length=256, verbose_name='openId')
    unionid = models.CharField(max_length=256, verbose_name='unionid')
    sex = models.CharField(max_length=2, choices=(('1', u'男'), ('2', u'女')), default='1', verbose_name='性别')
    province = models.CharField(max_length=32, verbose_name='省份', blank=True)
    city = models.CharField(max_length=32, verbose_name='城市',  blank=True)
    country = models.CharField(max_length=32, verbose_name='国家',  blank=True)
    headimgurl = models.CharField(max_length=512, verbose_name='头像地址')
    privilege = models.CharField(max_length=64, verbose_name='权限')
    address = models.CharField(max_length=64, verbose_name='地址', default='')
    phone_num = models.CharField(max_length=15, verbose_name='联系电话', default='')
    is_agent = models.BooleanField(default=False, verbose_name='代理商')
    join_time = models.DateTimeField(default=datetime.now, verbose_name='加入时间')

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.nickname


class AgentApply(models.Model):
    name = models.CharField(max_length=16, verbose_name='姓名')
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    is_handled = models.BooleanField(default=False,verbose_name='是否已处理')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '申请成为团长'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class AgentOrder(models.Model):
    group_buy = models.ForeignKey(GroupBuy, verbose_name='代理订单', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, verbose_name='代理人')
    goods_ids = models.CharField(max_length=64, verbose_name='选中的商品')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='申请时间')

    class Meta:
        verbose_name = '团长订单'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.id


class ShoppingCart(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='购买人')
    goods = models.ForeignKey(GroupBuyGoods, verbose_name='商品')
    agent_code = models.CharField(max_length=256, verbose_name='代理人code')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='购买时间')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.user.nickname + self.goods.goods.name


class GenericOrder(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='购买人')
    agent_code = models.CharField(max_length=256, verbose_name='代理人code')
    goods = models.ForeignKey(GroupBuyGoods, verbose_name='商品', default=1)
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='购买时间')
    status = models.BooleanField(default=True, verbose_name='取消状态')

    class Meta:
        verbose_name = '普通订单'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.id

