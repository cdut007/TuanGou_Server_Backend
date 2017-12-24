# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.

class Banner(models.Model):
    name = models.CharField(max_length=24, verbose_name=u'名称', default='')
    image = models.ImageField(upload_to='images/Banner', default='image/Banner/default.png', max_length=100, verbose_name=u'Banner')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'add time')
    is_show = models.BooleanField(default=True,verbose_name='is show')

    class Meta:
        verbose_name = u'Banner'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class GoodsClassify(models.Model):
    name = models.CharField(max_length=64, verbose_name=u'名称')
    desc = models.CharField(max_length=256, verbose_name='描述',default='')
    icon = models.ImageField(upload_to='images/Classify', verbose_name='图标', default='')
    image = models.ImageField(upload_to='images/Classify', verbose_name='图片', default='')
    created_by = models.CharField(max_length=64, default='')

    class Meta:
        verbose_name = u'商品类别'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class GroupBuy(models.Model):
    title = models.CharField(max_length=64, verbose_name='标题', default='')
    goods_classify = models.ForeignKey(GoodsClassify, related_name='group_buy',
                                       on_delete=models.CASCADE, verbose_name=u'商品类别')
    on_sale = models.BooleanField(default=False, verbose_name='是否上架')
    end_time = models.DateTimeField(default=datetime.now, verbose_name='结束时间')
    ship_time = models.DateField(default=datetime.now, verbose_name='发货时间')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    eyu = models.CharField(max_length=64, default='')
    created_by = models.CharField(max_length=64, default='')
    award_red_packets = models.CharField(max_length=2, default='0')
    rp_number = models.PositiveSmallIntegerField(default=0)
    min_rp_money = models.DecimalField(max_digits=4, decimal_places=2, default=None)
    max_rp_money = models.DecimalField(max_digits=4, decimal_places=2, default=None)
    min_order_amount = models.DecimalField(max_digits=6, decimal_places=2, default=None)

    class Meta:
        verbose_name = u'团购'
        verbose_name_plural = verbose_name

    def is_end(self):
        return datetime.now() >= self.end_time
    is_end.boolean = True
    is_end.short_description = u'是否截团'

    def __unicode__(self):
        return  str(self.id) + '_' + self.title


class Goods(models.Model):
    name = models.CharField(max_length=32, verbose_name=u'名称')
    desc = models.TextField(verbose_name='描述', default='')
    default_price = models.FloatField(default=0)
    default_stock =  models.PositiveIntegerField(default=0)
    default_unit = models.CharField(max_length=64, default='')
    created_by = models.CharField(max_length=64, default='')
    set = models.CharField(max_length=64, default='')
    brief_desc = models.CharField(max_length=128, default='')

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
    image = models.ImageField(upload_to='images/Goods/%Y-%m',default='image/Goods/default.png', max_length=100, verbose_name=u'商品图片')
    is_primary = models.BooleanField(default=False, verbose_name='是否显示在列表页')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = u'商品图片'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return str(self.id) + '-' + self.goods.name
