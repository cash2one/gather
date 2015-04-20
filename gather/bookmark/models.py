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
        verbose_name_plural = '书签列表'


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


class NotePad(models.Model):
    """ 便签"""
    user = models.ForeignKey(User, related_name='notes')
    title = models.CharField('便签标题', max_length=50, null=True, blank=True)
    comment = models.CharField('评论', max_length=50, null=True, blank=True,)
    parent_id = models.IntegerField('所属评论下得评论', null=True, blank=True, default=0)
    parent_note_id = models.IntegerField('所属便签', null=True, blank=True, default=0)
    reply_to = models.ForeignKey(User, related_name='replys', null=True)
    read_sum = models.IntegerField('点击次数', default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间')

    class Meta:
        verbose_name = '便签信息'
        verbose_name_plural = '便签列表'

    def is_special_care(self, user=None):
        """ 是否特别关心该用户"""
        if user.is_authenticated():
            return SpecialCare.objects.filter(user=user, care=self.user, is_valid=True).exists()
        else:
            return False

    def is_self_note(self, user=None):
        """ 是否是自己的状态"""
        if user.is_authenticated():
            return self.user.id == user.id
        else:
            # 非登录用户与自己的状态不显示特别关心
            return True

    def get_owner_photo(self):
        """ 获取状态所有者的头像"""
        try:
            return self.user.profile.big_photo.url
        except:
            return '/static/images/default_head.png'


class NoteHeart(models.Model):
    """ 便签中'喜欢'信息"""
    user = models.ForeignKey(User, related_name='hearts')
    note = models.ForeignKey(NotePad, related_name='hearts')
    is_still = models.BooleanField('是否仍喜欢', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '点赞信息'
        verbose_name_plural = '点赞列表'


class SpecialCare(models.Model):
    """ 特别关心对应关系"""
    user = models.ForeignKey(User)
    care = models.ForeignKey(User, related_name='cares')

    is_valid = models.BooleanField('是否有效', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '特别关心信息'
        verbose_name_plural = '特别关心列表'
