#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'gather.views.index', name='index'),
    url(r'^account/', include('account.urls')),
    url(r'^bookmark/', include('bookmark.urls')),

)
