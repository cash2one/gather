#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('wash.mviews',
    url(r'^$', 'manage_login', name='wash_manage_login'),
    url(r'^logout/$', 'manage_logout', name='wash_manage_logout'),
    url(r'^index/$', 'manage_index', name='wash_manage_index'),

    url(r'^model/(?P<model_type>\D+)/del/(?P<type_id>\d+)/$', 'model_del', name='manage_model_del'),

    url(r'^user/$', 'user_list', name='manage_user_list'),

    # 洗刷清单
    url(r'^type/$', 'wash_type', name='manage_wash_type'),
    url(r'^type/add/$', 'wash_type_add', name='manage_wash_type_add'),
    url(r'^type/update/(?P<type_id>\d+)/$', 'wash_type_update', name='manage_wash_type_update'),

    # 优惠券
    url(r'^discount/$', 'discount', name='manage_discount'),
    url(r'^discount/add/$', 'discount_add', name='manage_discount_add'),
    url(r'^discount/update/(?P<discount_id>\d+)/$', 'discount_update', name='manage_discount_update'),

    # 订单概览
    url(r'^order/$', 'order', name='manage_order'),

    # 订单详情
    url(r'^order/detail/(?P<order_id>\d+)/$', 'order_detail', name='manage_order_detail'),


)
