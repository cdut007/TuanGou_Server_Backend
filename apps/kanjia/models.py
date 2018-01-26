# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from decimal import Decimal
import random
from utils.common import random_str
from market.models import GroupBuy
from random import Random

class KanJiaActivity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    goods_image = models.CharField(max_length=128)
    original_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    activity_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    exchange_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    min_kj_money = models.DecimalField(max_digits=4, decimal_places=2, default=None)
    max_kj_money = models.DecimalField(max_digits=4, decimal_places=2, default=None)
    goods_description = models.CharField(max_length=32)
    end_time = models.DateTimeField()
    quantity = models.PositiveIntegerField(blank=True, null=True)
    activity_description = models.CharField(max_length=256)
    activity_introduction = models.TextField()
    purchase_limitation = models.PositiveSmallIntegerField(blank=True, null=True)
    need_subscribe = models.BooleanField(default=True)
    create_on = models.DateTimeField()

    class Meta:
        db_table = 'kj_activity'


class ActivityJoin(models.Model):
    aj_id = models.AutoField(primary_key=True)
    owner = models.PositiveIntegerField()
    activity_id = models.PositiveIntegerField()
    current_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    create_on = models.DateTimeField()

    class Meta:
        db_table = 'kj_activity_join'

    @staticmethod
    def join(owner, activity_id):
        activity = KanJiaActivity.objects.get(activity_id=activity_id)
        join_record = ActivityJoin.objects.filter(owner=owner, activity_id=activity_id).first()
        if join_record: return
        ActivityJoin.objects.create(
            owner = owner,
            activity_id = activity_id,
            current_price = activity.original_price,
            create_on = datetime.now()
        )


class KanJiaLog(models.Model):
    kjl_id = models.AutoField(primary_key=True)
    owner = models.PositiveIntegerField()
    kj_user = models.PositiveIntegerField()
    activity_id = models.PositiveIntegerField(default=None)
    money = models.DecimalField(max_digits=4, decimal_places=2, default=None)
    current_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    create_on = models.DateTimeField()

    class Meta:
        db_table = 'kj_activity_log'

    @staticmethod
    def kan_jia(owner, kj_user, activity_id):
        activity = KanJiaActivity.objects.get(activity_id=activity_id)
        activity_join = ActivityJoin.objects.filter(activity_id=activity_id, owner=owner).first()

        a = activity_join.current_price - activity.activity_price
        if a<=0: return 0

        kj_money = KanJiaLog.gen_kj_money(activity.min_kj_money, activity.max_kj_money)
        if kj_money > a: kj_money = a

        current_price = activity_join.current_price - kj_money
        KanJiaLog.objects.create(
            owner = owner,
            kj_user = kj_user,
            activity_id = activity_id,
            money = kj_money,
            current_price = current_price,
            create_on = datetime.now()
        )
        activity_join.current_price = current_price
        activity_join.save()
        return kj_money

    @staticmethod
    def gen_kj_money(min_money, max_money):
        return Decimal(random.uniform(float(min_money), float(max_money))).quantize(Decimal('0.00'))

    @staticmethod
    def is_kan_guo(owner, kj_user, activity_id):
        log = KanJiaLog.objects.filter(owner=owner, kj_user=kj_user,activity_id=activity_id).first()
        return log

    @staticmethod
    def times_today(kj_user):
        today = datetime.now()
        today_start = "{Y}-{m}-{d} 00:00:00".format(Y=today.year, m=today.month, d=today.day)
        today_start = datetime.strptime(today_start, '%Y-%m-%d %H:%M:%S')
        today_end = "{Y}-{m}-{d} 23:59:59".format(Y=today.year, m=today.month, d=today.day)
        today_end = datetime.strptime(today_end, '%Y-%m-%d %H:%M:%S')
        count = KanJiaLog.objects.filter(
            kj_user = kj_user,
            create_on__gt = today_start,
            create_on__lt = today_end
        ).count()
        return count


class KanJiaOrder(models.Model):
    order_id = models.AutoField(primary_key=True)
    owner = models.PositiveIntegerField()
    activity_id = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()
    exchange_price = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    pay_money = models.PositiveIntegerField()
    trade_no = models.CharField(max_length=32)
    prepay_id = models.CharField(max_length=64)
    wx_bank_type = models.CharField(max_length=32)
    wx_result_code = models.CharField(max_length=24)
    wx_err_code = models.CharField(max_length=32)
    wx_err_code_des = models.CharField(max_length=256)
    wx_transaction_id = models.CharField(max_length=32)
    pickup_code = models.CharField(max_length=24)
    create_on = models.DateTimeField()

    class Meta:
        db_table = 'kj_order'

    @staticmethod
    def prepay(owner, activity_id, quantity, exchange_price, pay_money,trade_no, prepay_id):
        KanJiaOrder.objects.create(
            owner = owner,
            activity_id = activity_id,
            quantity = quantity,
            exchange_price = exchange_price,
            pay_money = pay_money,
            trade_no = trade_no,
            prepay_id = prepay_id,
            create_on = datetime.now()
        )

    @staticmethod
    def gen_trade_no():
        no = KanJiaOrder.random_str()
        rec = KanJiaOrder.objects.filter(trade_no=no).first()
        if rec: return KanJiaOrder.gen_trade_no()
        return no

    @staticmethod
    def random_str():
        string = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZ0123456789_-*'
        for i in range(28):
            string += chars[Random().randint(0, len(chars) - 1)]
        return string

    def update_pay(self):
        pass

