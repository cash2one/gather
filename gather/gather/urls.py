#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'gather.views.index', name='index'),
    url(r'^share/', include('share.urls')),
    url(r'^help/', include('help.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^bookmark/', include('bookmark.urls')),
    url(r'^comment/', include('comment.urls')),
    url(r'^wechat/', include('wechat.urls')),
    url(r'^wash/', include('wash.urls')),
    url(r'^wash/manage/', include('wash.murls')),
    url(r'^abount_us/', 'gather.views.about_us', name='about_us'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
