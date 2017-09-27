# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models


class WinXinCache(models.Model):
    cache_key = models.CharField(max_length=64)
    cache_value = models.CharField(max_length=512)
    expire_date = models.DateTimeField(blank=True)

    class Meta:
        db_table = 'lg_weixin_cache'