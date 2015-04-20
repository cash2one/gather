#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from share.models import Share


class ShareAdmin(admin.ModelAdmin):
    """ 拜托列表"""
    list_display = ('user', 'title', 'created')
    search_fields = ['user']
    ordering = ['-created']

admin.site.register(Share, ShareAdmin)
