# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.

class Banner(models.Model):
    image = models.ImageField(upload_to='images/%Y/%m', default='image/default.png', max_length=100, verbose_name=u'轮播图')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    is_show = models.BooleanField(default=True,verbose_name='是否显示')

    class Meta:
        verbose_name = u'轮播图'
        verbose_name_plural = verbose_name


class GoodsClassify(models.Model):
    name = models.CharField(max_length=24, verbose_name=u'名称')

    class Meta:
        verbose_name = u'商品类别'
        erbose_name_plural = verbose_name


class GroupBuy(models.Model):
    goods_classify = models.ForeignKey(GoodsClassify, verbose_name=u'商品类别')
    start_time = models.DateTimeField(default=datetime.now, verbose_name='开团时间')
    end_time = models.DateTimeField(default=datetime.now, verbose_name='结束时间')

    class Meta:
        verbose_name = u'团购'
        erbose_name_plural = verbose_name


class GroupBuyGoods(models.Model):
    group_buy = models.ForeignKey(GroupBuy, verbose_name='团购')
    goods = models.ForeignKey(Goods, verbose_name='商品')
    price = models.FloatField(max)



class Goods(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'名称')

    class Meta:
        verbose_name = u'商品'
        erbose_name_plural = verbose_name


class GoodsGallery(models.Model):
    goods = models.ForeignKey(Goods, verbose_name='商品')
    image = models.ImageField(upload_to='images/%Y/%m',default='image/default.png', max_length=100, verbose_name=u'商品图片')
    is_primary = models.BooleanField(default=False, verbose_name='是否显示在列表页')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = u'商品图集'
        erbose_name_plural = verbose_name