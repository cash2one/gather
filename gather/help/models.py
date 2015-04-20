#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Help(models.Model):
    """ 帮助信息"""
    seeker = models.ForeignKey(User, related_name='seekers')
    helper = models.ForeignKey(User, related_name='helpers', blank=True, null=True)
    title = models.CharField('标题', max_length=50)
    content = models.TextField('求助内容')
    connect_method = models.CharField('联系方式', max_length=50)
    remark = models.TextField('备注', blank=True, null=True)

    longitude = models.FloatField('经度')
    latitude = models.FloatField('维度')

    is_valid = models.BooleanField('是否有效', default=True)
    is_succ = models.BooleanField('是否帮助成功', default=True)
    succ_time = models.DateTimeField('成功时间', blank=True, null=True)
    cancel_time = models.DateTimeField('撤销时间', blank=True, null=True)
    invalid_time = models.DateTimeField('失效时间', blank=True, null=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '帮助信息'
        verbose_name_plural = '帮助信息列表'

    def is_self(self, user=None):
        """ 是否为自己发布"""
        if user.is_authenticated():
            if user.id == self.seeker.id:
                return True
            else:
                return False
        else:
            return True

    
