#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from bookmark.models import BookMark, Label, NotePad


class BookMarkAdmin(admin.ModelAdmin):
    """ 书签列表"""
    list_display = ('user', 'title', 'created')
    search_fields = ['user__username', 'title']
    readonly_fields = ('created',)

admin.site.register(BookMark, BookMarkAdmin)


class LabelAdmin(admin.ModelAdmin):
    """ 标签列表"""
    list_display = ('name', 'created')
    search_fields = ['name']
    readonly_fields = ('created',)

admin.site.register(Label, LabelAdmin)


class NotePadAdmin(admin.ModelAdmin):
    """ 便签列表"""
    list_display = ('user', 'title', 'read_sum', 'created')
    search_fields = ['user__username', 'title']
    readonly_fields = ('created',)

admin.site.register(NotePad, NotePadAdmin)



