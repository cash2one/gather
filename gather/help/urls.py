#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('help.views',
    url(r'^$', 'help', name='help'),
    url(r'^add/$', 'help_add', name='help_add'),
    url(r'^points/$', 'help_points', name='help_points'),
    url(r'^detail/(?P<help_id>\d+)/$', 'help_detail', name='help_detail'),
)

