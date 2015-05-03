#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from comment.models import ShareComment, NoteComment, HelpComment, Heart


class ShareAdmin(admin.ModelAdmin):
    """ 分享评论"""
    list_display = ('user', 'reply_to', 'comment')
    search_fields = ['user']
    ordering = ['-created']

admin.site.register(ShareComment, ShareAdmin)


class NoteAdmin(admin.ModelAdmin):
    """ 便签评论"""
    list_display = ('user', 'reply_to', 'comment')
    search_fields = ['user']
    ordering = ['-created']

admin.site.register(NoteComment, NoteAdmin)


class HelpAdmin(admin.ModelAdmin):
    """ 帮助评论"""
    list_display = ('user', 'reply_to', 'comment')
    search_fields = ['user']
    ordering = ['-created']

admin.site.register(HelpComment, HelpAdmin)

class HeartAdmin(admin.ModelAdmin):
    """ 点赞列表"""
    list_display = ('user', 'note_title', 'created', 'is_still')
    search_fields = ['user__username', 'note__title']
    readonly_fields = ('created',)

    def note_title(self, obj):
        return obj.note.title

    note_title.allow_tags = True
    note_title.short_description = u'便签标题'

admin.site.register(Heart, HeartAdmin)
