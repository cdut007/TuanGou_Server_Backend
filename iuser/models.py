# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserProfile(models.Model):
    nickname = models.CharField(max_length=64, verbose_name=u'昵称')
    openid = models.CharField(max_length=256, verbose_name='openId')
    unionid = models.CharField(max_length=256, verbose_name='unionid')
    sex = models.CharField(max_length=10, choices=(('male', u'男'), ('female', u'女')), default='male', verbose_name='性别')
    province = models.CharField(max_length=32, verbose_name='省份')
    city = models.CharField(max_length=32, verbose_name='城市')
    country = models.CharField(max_length=32, verbose_name='国家')
    headimgurl = models.CharField(max_length=512, verbose_name='头像地址')
    privilege = models.CharField(max_length=64, verbose_name='权限')
    join_time = models.DateTimeField(default=datetime.now, verbose_name='加入时间')

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.nickname
