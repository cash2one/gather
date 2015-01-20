#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from bookmark.models import BookMark, Label, NotePad, NoteHeart


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
    list_display = ('user', 'title', 'comment', 'read_sum', 'created')
    search_fields = ['user__username', 'title']
    readonly_fields = ('created',)

admin.site.register(NotePad, NotePadAdmin)


class NoteHeartAdmin(admin.ModelAdmin):
    """ 点赞列表"""
    list_display = ('user', 'note_title', 'created', 'is_still')
    search_fields = ['user__username', 'note__title']
    readonly_fields = ('created',)

    def note_title(self, obj):
        return obj.note.title

    note_title.allow_tags = True
    note_title.short_description = u'便签标题'

admin.site.register(NoteHeart, NoteHeartAdmin)

