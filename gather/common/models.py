#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Label(models.Model):
    """ 标签信息"""
    user_id = models.IntegerField(null=True, blank=True, default='0')
    name = models.CharField('标签名称', max_length=50)
    parent_id = models.IntegerField('父标签', null=True, blank=True, default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '标签信息'
        verbose_name_plural = '标签列表'

