#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('comment.views',
    url(r'^detail/(?P<obj_type>[a-z]{4})/(?P<obj_id>\d+)/', 'comments', name='comments'),
    url(r'^special_care/(?P<user_id>\d+)/', 'special_care', name='special_care'),
    url(r'^add/(?P<obj_type>[a-z]{4})/', 'add_comment', name='add_comment'),
    url(r'^heart/(?P<obj_type>[a-z]{4})/(?P<obj_id>\d+)/', 'heart', name='heart'),
)

