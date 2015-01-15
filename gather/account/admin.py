#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from account.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    """ 用户列表"""
    list_display = ('username', 'created')
    search_fields = ['username']
    ordering = ['-created']

admin.site.register(UserProfile, UserProfileAdmin)
