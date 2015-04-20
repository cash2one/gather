#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from help.models import Help


class HelpAdmin(admin.ModelAdmin):
    """ 拜托列表"""
    list_display = ('seeker', 'title', 'created')
    search_fields = ['seeker']
    ordering = ['-created']

admin.site.register(Help, HelpAdmin)
