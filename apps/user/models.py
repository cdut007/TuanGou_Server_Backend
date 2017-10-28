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