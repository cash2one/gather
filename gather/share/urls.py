#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('share.views',
    url(r'^$', 'share', name='share'),
    url(r'^add/$', 'add_share', name='add_share'),
    url(r'^(?P<share_id>\d+)/detail/$', 'detail_share', name='detail_share'),
)

