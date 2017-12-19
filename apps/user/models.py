# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from decimal import Decimal
import random

class ConsumerOrderRemarks(models.Model):
    id = models.AutoField(primary_key=True)
    group_buying_id = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField()
    merchant_code = models.CharField(max_length=128, default='')
    remark = models.CharField(max_length=2048)
    add_time = models.DateTimeField()

    class Meta:
        db_table = 'lg_consumer_order_remarks'
        unique_together = (("merchant_code", "group_buying_id", "user_id"),)


class MerchantPushLog(models.Model):
    id = models.AutoField(primary_key=True)
    group_buying_id = models.PositiveIntegerField()
    merchant_id = models.PositiveIntegerField()
    is_send_take_goods_notification = models.SmallIntegerField(default=0)
    is_send_excel = models.SmallIntegerField(default=0)
    excel_path = models.CharField(max_length=96, default='')

    @staticmethod
    def insert_send_excel_log(group_buying_id, merchant_id, excel_path):
        push_log = MerchantPushLog.objects.filter(group_buying_id=group_buying_id, merchant_id=merchant_id).first()
        if push_log:
            push_log.is_send_excel = 1
            push_log.excel_path = excel_path
            push_log.save()
        else:
            MerchantPushLog.objects.create(
                group_buying_id = group_buying_id,
                merchant_id = merchant_id,
                is_send_excel = 1,
                excel_path = excel_path
            )

    @staticmethod
    def insert_send_take_goods_notification(group_buying_id, merchant_id):
        push_log = MerchantPushLog.objects.filter(group_buying_id=group_buying_id, merchant_id=merchant_id).first()
        if push_log:
            push_log.is_send_take_goods_notification = 1
            push_log.save()
        else:
            MerchantPushLog.objects.create(
                group_buying_id = group_buying_id,
                merchant_id = merchant_id,
                is_send_take_goods_notification = 1
            )

    class Meta:
        db_table = 'lg_merchant_push_log'


class UnpackRedPacketsLog(models.Model):
    id = models.AutoField(primary_key=True)
    receiver = models.PositiveIntegerField(blank=False)
    unpack_user = models.PositiveIntegerField(null=True)
    get_from = models.PositiveIntegerField(null=True, blank=False)
    group_buying_id = models.PositiveIntegerField(blank=False)
    money = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    is_failure = models.CharField(max_length=2, default=0)
    failure_reason = models.CharField(max_length=4, null=True)
    is_send = models.CharField(max_length=2, blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    unpack_time = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def gen_four_record(receiver, group_buying_id):
        rps = [UnpackRedPacketsLog(receiver=receiver, group_buying_id=group_buying_id) for i in range(4)]
        UnpackRedPacketsLog.objects.bulk_create(rps)

    @staticmethod
    def unpack_one_rp(receiver, group_buying_id, unpack_user):
        blank_rp = UnpackRedPacketsLog.objects.filter(
            receiver=receiver,
            group_buying_id=group_buying_id,
            unpack_user__isnull=True
        ).first()
        if blank_rp:
            money = UnpackRedPacketsLog.gen_rp_money()
            blank_rp.unpack_user = unpack_user
            blank_rp.money = money
            blank_rp.unpack_time = datetime.now()
            blank_rp.save()
            return money
        else:
            return 0

    @staticmethod
    def gen_rp_money():
        return str(Decimal(random.uniform(0.2, 0.6)).quantize(Decimal('0.00')))

    @staticmethod
    def can_unpack(receiver, group_buying_id, unpack_user):
        rp_record = UnpackRedPacketsLog.objects.filter(
            receiver=receiver,
            group_buying_id=group_buying_id,
            unpack_user = unpack_user
        ).first()
        if rp_record:
            return 0
        else:
            return 1

    class Meta:
        db_table = 'lg_unpack_red_packets_log'


class WeiXinRpSendLog(models.Model):
    id = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=124)
    send_time = models.DateTimeField()
    mch_billno = models.CharField(max_length=32)
    money = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    return_code = models.CharField(max_length=16)
    return_msg = models.CharField(max_length=128)
    err_code = models.CharField(max_length=16)
    err_code_des = models.CharField(max_length=128)
    status = models.CharField(max_length=16, blank=True, null=True)