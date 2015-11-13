# !/usr/bin/python
#  -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class WeToken(models.Model):
    """ 微信Token"""
    token = models.CharField('ServerToken', max_length=1024, null=True, blank=True)
    expire_time = models.IntegerField('Expire_time', max_length=1024, null=True, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)


class WeProfile(models.Model):
    """ 微信登录帐号的信息"""
    UNKNOW = 0
    MAN = 1
    WOMEN = 2

    SEX = (
        (UNKNOW, '未知'),
        (MAN, '男'),
        (WOMEN, '女'),
    )

    user = models.OneToOneField(User, related_name='we_profile', null=True, default=None)
    username = models.CharField('用户名', max_length=30, null=True, blank=True)
    open_id = models.CharField('open_id', max_length=30, unique=True)
    nick_name = models.CharField('昵称', max_length=50, null=True, blank=True)
    sex = models.IntegerField('性别', max_length=1, choices=SEX, default=UNKNOW, null=True, blank=True)
    city = models.CharField('城市', max_length=50, null=True, blank=True)
    country = models.CharField('国家', max_length=30, null=True, blank=True)
    province = models.CharField('省', max_length=30, null=True, blank=True)
    language = models.CharField('使用语言', max_length=20, null=True, blank=True)
    subscribe_time = models.DateTimeField('上次关注时间', null=True, blank=True)
    headimgurl = models.CharField('头像URL', max_length=300, null=True, blank=True)

    is_subscribed = models.BooleanField('是否关注', default=True)
    is_binded = models.BooleanField('是否已经绑定微信', default=False)
    is_pwd_reset = models.BooleanField('是否重置初始密码', default=False)
    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '微信用户信息'
        verbose_name_plural = '微信用户信息列表'


class WeLoginQR(models.Model):
    """ 微信扫描登录"""
    ticket = models.CharField('ticket', max_length=100, null=True, blank=True)
    open_id = models.CharField('open_id', max_length=50, null=True, blank=True)
    is_used = models.BooleanField('是否以使用', default=False)
    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)
