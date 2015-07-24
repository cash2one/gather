#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class ChatInfo(models.Model):
    """ 聊天内容信息"""
    user = models.ForeignKey(User, related_name='chats', null=True)
    uuid = models.CharField('唯一标示', max_length=50)
    nickname = models.CharField('匿名', max_length=30, null=True, blank=True)
    content = models.CharField('内容', max_length=300, null=True, blank=True)
    photo = models.IntegerField('头像序列数')

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '聊天内容信息'
        verbose_name_plural = '聊天内容信息列表'
