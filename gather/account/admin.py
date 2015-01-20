#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from account.models import UserProfile, LoginLog, ClickLog


class UserProfileAdmin(admin.ModelAdmin):
    """ 用户列表"""
    list_display = ('username', 'created')
    search_fields = ['username']
    ordering = ['-created']

admin.site.register(UserProfile, UserProfileAdmin)


class LoginLogAdmin(admin.ModelAdmin):
    """ 登录日志列表"""
    list_display = ('username', 'login_ip', 'login_time', 'is_succ')
    search_fields = ['username']
    ordering = ['-login_time']

admin.site.register(LoginLog, LoginLogAdmin)


class ClickLogAdmin(admin.ModelAdmin):
    """ 用户点击纪录列表"""
    list_display = ('username', 'click_url', 'click_time')
    search_fields = ['username']
    ordering = ['-click_time']
    
admin.site.register(ClickLog, ClickLogAdmin)
