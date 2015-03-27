#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('help.views',
    url(r'^$', 'help', name='help'),
)

