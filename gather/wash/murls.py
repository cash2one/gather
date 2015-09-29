#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wash.mviews',
    url(r'^$', 'manage_login', name='wash_manage_login'),
    url(r'^logout/$', 'manage_logout', name='wash_manage_logout'),
    url(r'^index/$', 'manage_index', name='wash_manage_index'),
    # 洗刷清单
    url(r'^type/$', 'wash_type', name='manage_wash_type'),
    url(r'^type/add/$', 'wash_type_add', name='manage_wash_type_add'),
    url(r'^type/update/(?P<type_id>\d+)/$', 'wash_type_update', name='manage_wash_type_update'),

)
