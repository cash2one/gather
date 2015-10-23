#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wash.views',
    url(r'^$', 'index', name='wash_index'),
    url(r'^code/$', 'verify_code_img', name='verify_code_img'),
    url(r'^oauth/$', 'oauth', name='oauth'),
    url(r'^check_code/$', 'verify_code_check', name='verify_code_check'),
    url(r'^show/$', 'show', name='wash_show'),
    url(r'^regist/$', 'regist', name='wash_regist'),
    url(r'^verify/$', 'verify_code', name='wash_verify'),

    url(r'^account/$', 'account', name='wash_account'),
    url(r'^order/$', 'order', name='wash_order'),
    url(r'^basket/$', 'basket', name='wash_basket'),
    url(r'^basket/update/$', 'basket_update', name='wash_basket_update'),

    url(r'^user/address/$', 'user_address', name='wash_user_address'),
    url(r'^user/address/select/$', 'user_address_select', name='wash_user_address_select'),
    url(r'^user/address/add/$', 'user_address_add', name='wash_user_address_add'),
    url(r'^address/street/$', 'address_street', name='wash_address_street'),
    url(r'^user/address/update/(?P<address_id>\d+)/$', 'user_address_update', name='wash_user_address_update'),

    url(r'^user/order/$', 'user_order', name='wash_user_order'),
    url(r'^user/order/detail/(?P<order_id>\d+)/$', 'user_order_detail', name='wash_user_order_detail'),
    url(r'^user/order/cancel/(?P<order_id>\d+)/$', 'user_order_cancel', name='wash_user_order_cancel'),
    url(r'^user/discount/$', 'user_discount', name='wash_user_discount'),

)
