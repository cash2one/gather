#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """ 用户注册信息"""
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    username = models.CharField('用户名', max_length=30, unique=True)
    nickname = models.CharField('昵称', max_length=30, null=True, blank=True)
    email = models.EmailField('email', max_length=100, null=True, blank=True)
    is_mail_verified = models.BooleanField('是否已经通过验证', default=False)
    mail_verified_date = models.DateTimeField('邮箱通过验证时间', blank=True, null=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户详细信息'
        verbose_name_plural = '用户详细信息列表'

    def __unicode__(self):
        return self.username

    def get_mask_username(self):
        # 用户名保密
        return self.username[:3] + "******"

    def get_mask_email(self):
        # 邮箱保密
        try:
            return self.email[:3] + '****' + self.email[self.email.find('@'):]
        except:
            return None

