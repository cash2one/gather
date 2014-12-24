#!/usr/bin/python
# -*- coding:utf-8 -*-

from django.contrib import admin

from config.models import IndexImg, IndexText


class IndexImgAdmin(admin.ModelAdmin):
    fields = ('index_img', 'img_name', 'image_tag', 'is_show', 'link_url', 'created', 'updated', 'ordering',)
    list_display = ('img_name', 'is_show', 'ordering', 'link_url')
    readonly_fields = ('image_tag', 'created', 'updated')


class IndexTextAdmin(admin.ModelAdmin):
    fields = ('title', 'is_show', 'content')
    list_display = ('title', 'is_show', 'created')

admin.site.register(IndexImg, IndexImgAdmin)
admin.site.register(IndexText, IndexTextAdmin)

