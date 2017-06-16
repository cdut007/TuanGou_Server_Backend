# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.

class Banner(models.Model):
    name = models.CharField(max_length=24, verbose_name=u'名称', default='')
    image = models.ImageField(upload_to='images/%Y/%m', default='image/default.png', max_length=100, verbose_name=u'Banner')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'add time')
    is_show = models.BooleanField(default=True,verbose_name='is show')

    class Meta:
        verbose_name = u'Banner'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class GoodsClassify(models.Model):
    name = models.CharField(max_length=24, verbose_name=u'名称')
    desc = models.CharField(max_length=256, verbose_name='描述',default='')
    icon = models.ImageField(upload_to='images/%Y/%m', verbose_name='图标', default='')
    image = models.ImageField(upload_to='images/%Y/%m', verbose_name='图片', default='')

    class Meta:
        verbose_name = u'商品类别'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class GroupBuy(models.Model):
    title = models.CharField(max_length=64, verbose_name='标题', default='')
    goods_classify = models.ForeignKey(GoodsClassify, related_name='group_buy',
                                       on_delete=models.CASCADE, verbose_name=u'商品类别')
    start_time = models.DateTimeField(default=datetime.now, verbose_name='开团时间')
    end_time = models.DateTimeField(default=datetime.now, verbose_name='结束时间')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = u'团购'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.title


class Goods(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'名称')

    class Meta:
        verbose_name = u'商品'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class GroupBuyGoods(models.Model):
    group_buy = models.ForeignKey(GroupBuy,  related_name='group_buy_goods', verbose_name='团购')
    goods = models.ForeignKey(Goods,verbose_name='商品')
    price = models.FloatField(verbose_name='价格')
    stock = models.PositiveIntegerField(verbose_name='库存', default=0)
    brief_dec = models.CharField(max_length=64, verbose_name='单位描述', default='')

    class Meta:
        verbose_name = u'团购商品'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.group_buy.title + '-' + self.goods.name


class GoodsGallery(models.Model):
    goods = models.ForeignKey(Goods, related_name='images',verbose_name='商品')
    image = models.ImageField(upload_to='images/%Y/%m',default='image/default.png', max_length=100, verbose_name=u'商品图片')
    is_primary = models.BooleanField(default=False, verbose_name='是否显示在列表页')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = u'商品图集'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.goods.name


class Order(models.Model):
    pass