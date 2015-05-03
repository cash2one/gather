#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('bookmark.views',
    url(r'^$', 'bookmark', name='bookmark'),
    url(r'^import/$', 'import_bookmark', name='import_bookmark'),  # 导入html书签

    url(r'^note/$', 'note', name='note'),
)

