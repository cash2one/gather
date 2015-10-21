#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('wechat.views',
    url(r'^$', 'index'),
    url(r'^oauth/code/$', 'code_get_openid'),
)
