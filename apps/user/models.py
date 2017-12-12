# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

from django.db import models


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


class ConsumerOrderSharingSummary(models.Model):
    id = models.AutoField(primary_key=True)
    sharing_code = models.CharField(max_length=128, default='')
    group_buying_id = models.PositiveIntegerField()
    consumer_bought_count = models.PositiveSmallIntegerField()