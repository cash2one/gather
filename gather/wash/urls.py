#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wash.views',
    url(r'^$', 'index', name='wash_index'),
    url(r'^show/$', 'show', name='wash_show'),
    url(r'^regist/$', 'regist', name='wash_regist'),
    url(r'^verify/$', 'verify_code', name='wash_verify'),

    url(r'^account/$', 'account', name='wash_account'),
)
