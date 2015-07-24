#!/usr/bin/python
#! -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Detail(models.Model):
    """ 评论详情"""
    comment = models.CharField('评论', max_length=50, null=True, blank=True,)
    parent_comment_id = models.IntegerField('评论下的评论', null=True, blank=True, default=0)
    parent_obj_id = models.IntegerField('所属根', null=True, blank=True, default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        abstract = True


class NoteComment(Detail):
    """ note上得评论"""
    user = models.ForeignKey(User, related_name='note_comments')
    reply_to = models.ForeignKey(User, related_name='note_replys', null=True)

    class Meta:
        verbose_name = 'note评论详情'
        verbose_name_plural = 'note评论详情列表'


class ShareComment(Detail):
    """ share上得评论"""
    user = models.ForeignKey(User, related_name='share_comments')
    reply_to = models.ForeignKey(User, related_name='share_replys', null=True)

    class Meta:
        verbose_name = 'share评论详情'
        verbose_name_plural = 'share评论详情列表'


class HelpComment(Detail):
    """ help上得评论"""
    user = models.ForeignKey(User, related_name='help_comments')
    reply_to = models.ForeignKey(User, related_name='help_replys', null=True)

    class Meta:
        verbose_name = 'help评论详情'
        verbose_name_plural = 'help评论详情列表'


class Heart(models.Model):
    """ 点赞信息"""
    user = models.ForeignKey(User, related_name='hearts')
    heart_id = models.IntegerField('点赞对象')
    is_still = models.BooleanField('是否仍喜欢', default=False)

    heart_type = models.CharField('点赞种类', max_length=10)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '点赞信息'
        verbose_name_plural = '点赞列表'
