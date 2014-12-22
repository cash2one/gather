#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('bookmark.views',
    url(r'^$', 'bookmark', name='bookmark'),
    

)

