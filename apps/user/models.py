# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from decimal import Decimal
import random
from utils.common import random_str
from market.models import GroupBuy

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

    class Meta:
        db_table = 'lg_merchant_push_log'

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


class UnpackRedPacketsLog(models.Model):
    id = models.AutoField(primary_key=True)
    receiver = models.PositiveIntegerField(blank=False)
    unpack_user = models.PositiveIntegerField(null=True)
    get_from = models.PositiveIntegerField(null=True, blank=False)
    group_buying_id = models.PositiveIntegerField(blank=False)
    money = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    is_failure = models.CharField(max_length=2, default=0)
    send_id = models.PositiveIntegerField(blank=True, null=True)
    unpack_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'lg_unpack_red_packets_log'

    @staticmethod
    def gen_rp_record(receiver, group_buying_id, get_from):
        group_buying = GroupBuy.objects.get(pk=group_buying_id)
        rps = [UnpackRedPacketsLog(
            receiver=receiver,
            group_buying_id=group_buying_id,
            get_from=get_from
        ) for i in range(group_buying.rp_number)]
        UnpackRedPacketsLog.objects.bulk_create(rps)
        return group_buying.rp_number

    @staticmethod
    def unpack_one_rp(receiver, group_buying_id, unpack_user):
        blank_rp = UnpackRedPacketsLog.objects.filter(
            receiver=receiver,
            group_buying_id=group_buying_id,
            unpack_user__isnull=True
        ).first()
        if blank_rp:
            money = UnpackRedPacketsLog.gen_rp_money(group_buying_id)
            blank_rp.unpack_user = unpack_user
            blank_rp.money = money
            blank_rp.unpack_time = datetime.now()
            blank_rp.save()
            return money
        else:
            return 0

    @staticmethod
    def re_activate_rp(receiver, group_buying_id, get_from):
        group_buying = GroupBuy.objects.get(pk=group_buying_id)
        UnpackRedPacketsLog.objects.filter(
            receiver=receiver,
            group_buying_id=group_buying_id,
            is_failure=2
        ).update(is_failure=0, get_from=get_from)
        return group_buying.rp_number

    @staticmethod
    def gen_rp_money(group_buying_id):
        group_buying = GroupBuy.objects.get(pk=group_buying_id)
        min_money = group_buying.min_rp_money
        max_money = group_buying.max_rp_money
        return str(Decimal(random.uniform(float(min_money), float(max_money))).quantize(Decimal('0.00')))

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

    @staticmethod
    def times_today(unpack_user):
        today = datetime.now()
        today_start = "{Y}-{m}-{d} 00:00:00".format(Y=today.year, m=today.month, d=today.day)
        today_start = datetime.strptime(today_start, '%Y-%m-%d %H:%M:%S')
        today_end = "{Y}-{m}-{d} 00:00:00".format(Y=today.year, m=today.month, d=today.day+1)
        today_end = datetime.strptime(today_end, '%Y-%m-%d %H:%M:%S')
        count = UnpackRedPacketsLog.objects.filter(
            unpack_user=unpack_user,
            unpack_time__gt=today_start,
            unpack_time__lt=today_end
        ).count()
        return count

    @staticmethod
    def update_send(group_buying_id, receiver, send_id):
        UnpackRedPacketsLog.objects.filter(
            receiver=receiver,
            group_buying_id=group_buying_id,
            is_failure=0
        ).update(send_id=send_id)


class WeiXinRpSendLog(models.Model):
    id = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=124)
    send_time = models.DateTimeField()
    mch_bill_no = models.CharField(max_length=32)
    money = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    result_code = models.CharField(max_length=16, blank=True, null=True)
    return_code = models.CharField(max_length=16)
    return_msg = models.CharField(max_length=128)
    err_code = models.CharField(max_length=16)
    err_code_des = models.CharField(max_length=128)
    status = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        db_table = 'lg_wei_xin_rp_send_log'

    @staticmethod
    def insert_one_log(open_id, money, bill_no, res):
        entry = WeiXinRpSendLog(
            openid = open_id,
            send_time = datetime.now(),
            mch_bill_no = bill_no,
            money = money,
            result_code = res['result_code'],
            return_code = res['return_code'],
            return_msg = res['return_msg'],
            err_code = res['err_code'],
            err_code_des = res['err_code_des'],
            status = 'RECEIVED'
        )
        entry.save()
        return entry.id

    @staticmethod
    def gen_bill_no():
        ra = random_str(random_length=28)
        rec = WeiXinRpSendLog.objects.filter(mch_bill_no = ra).first()
        if rec:
            return WeiXinRpSendLog.gen_bill_no()
        else:
            return ra