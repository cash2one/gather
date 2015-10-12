#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wash.views',
    url(r'^$', 'index', name='wash_index'),
    url(r'^show/$', 'show', name='wash_show'),
    url(r'^regist/$', 'regist', name='wash_regist'),
    url(r'^verify/$', 'verify_code', name='wash_verify'),

    url(r'^account/$', 'account', name='wash_account'),
    url(r'^order/$', 'order', name='wash_order'),
    url(r'^basket/$', 'basket', name='wash_basket'),
    url(r'^basket/update/$', 'basket_update', name='wash_basket_update'),

    url(r'^user/address/$', 'user_address', name='wash_user_address'),
    url(r'^user/address/add/$', 'user_address_add', name='wash_user_address_add'),
    url(r'^user/address/update/(?P<address_id>\d+)/$', 'user_address_update', name='wash_user_address_update'),
)
