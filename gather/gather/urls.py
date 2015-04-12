#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'gather.views.index', name='index'),
    url(r'^note/$', 'gather.views.note', name='note'),
    url(r'^share/', include('share.urls')),
    url(r'^help/', include('help.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^bookmark/', include('bookmark.urls')),

    url(r'^comment/add/', 'gather.views.add_comment', name='add_comment'),
    url(r'^comment/list/(?P<note_id>\d+)/', 'gather.views.comments', name='comments'),
    url(r'^note/heart/', 'gather.views.heart', name='heart'),
    url(r'^note/special_care/', 'gather.views.special_care', name='special_care'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
