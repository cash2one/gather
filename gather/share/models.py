#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User

from utils import get_image_x_y


class Share(models.Model):
    """ 分享信息"""
    user = models.ForeignKey(User, related_name='shares')

    title = models.CharField('标题', max_length=30)
    photo = models.ImageField(upload_to='share/%Y/%m/%d', blank=True, null=True)
    content = models.TextField('分享的简介信息', blank=True, null=True)
    read_sum = models.IntegerField('点击次数', default=0)
   
    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '分享信息'
        verbose_name_plural = '分享信息列表'

    def is_read(self):
        """ 是否已阅读"""
        return IsRead.objects.filter(share=self, is_active=True).exists()

    def can_show_desc(self):
        """ 能否显示简介"""
        if '<img' in self.content:
            return False
        else:
            return True

    def resize_photo(self):
        """ 重新设置展示大小"""
        xsize, ysize = get_image_x_y(self.photo)
        if xsize > 600:
            return (600, 600 * ysize / xsize)


class IsRead(models.Model):
    """ 是否已阅读"""
    user = models.ForeignKey(User, related_name='is_reads')
    share = models.ForeignKey(Share, related_name='shares')

    is_active = models.BooleanField('是否有效', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '已查看信息'
        verbose_name_plural = '已查看信息列表'



    
