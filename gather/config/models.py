#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models


class IndexImg(models.Model):
    """ 首页图片"""
    index_img = models.ImageField(upload_to="index_img")
    img_name = models.CharField('图片名称', default=u'无名', max_length=20)
    is_show = models.BooleanField('是否显示', default=False)
    link_url = models.CharField('图片链接到的地址', max_length=200, blank=True, null=True)
    ordering = models.IntegerField('图片轮播顺序', max_length=2)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = u"首页轮播图片"
        verbose_name_plural = u"首页轮播图片列表"

    def image_tag(self):
        return u'<img src="%s" />' % self.index_img.url

    image_tag.short_description = '首页轮播图片'
    image_tag.allow_tags = True


class IndexText(models.Model):
    """ 首页诗词"""
    title = models.CharField('名称', default=u'无名', max_length=20)
    is_show = models.BooleanField('是否显示', default=False)
    content = models.TextField('内容', default='惶惶然如有所失')

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = u"首页诗词"
        verbose_name_plural = u"首页诗词列表"
