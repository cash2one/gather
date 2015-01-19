#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class BookMark(models.Model):
    """ 书签信息"""
    user = models.ForeignKey(User, related_name='bookmarks')
    title = models.CharField('标题', max_length=150)
    url = models.CharField('url', max_length=300, null=True, blank=True)
    summary = models.CharField('摘要', max_length=300, null=True, blank=True, default='无')

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '书签信息'
        verbose_name_plural = '书签信息列表'


class Label(models.Model):
    """ 标签信息"""
    user_id = models.IntegerField(null=True, blank=True, default='0')
    name = models.CharField('标签名称', max_length=50)
    parent_id = models.IntegerField('父标签', null=True, blank=True, default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '标签信息'
        verbose_name_plural = '标签信息列表'


class NotePad(models.Model):
    """ 便签"""
    user = models.ForeignKey(User, related_name='notes')
    title = models.CharField('便签标题', max_length=50, null=True, blank=True)
    comment = models.CharField('评论', max_length=50, null=True, blank=True,)
    parent_id = models.IntegerField('所属评论下得评论', null=True, blank=True, default=0)
    read_sum = models.IntegerField('点击次数', default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '标签信息'
        verbose_name_plural = '标签信息列表'


class NoteHeart(models.Model):
    """ 便签中喜欢信息"""
    user = models.ForeignKey(User, related_name='hearts')
    note = models.ForeignKey(NotePad, related_name='hearts')
    is_still = models.BooleanField('是否仍喜欢', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '喜欢信息'
        verbose_name_plural = '喜欢信息列表'

   