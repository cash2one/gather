#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('account.views',
    url(r'^regist/$', 'regist', name='regist'),
    url(r'^login/$', 'login', name='login'),
    #url(r'^verify_code/$', 'verify_code', name='verify_code'),
    #url(r'^verify/$', 'verify', name='verify'),
    url(r'^resend_bind_email/$', 'resend_bind_email', name='resend_bind_email'),
    #url(r'^change_pwd/$', 'change_pwd', name='change_pwd'),
)