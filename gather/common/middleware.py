#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import get_cache
from django.utils.importlib import import_module

from utils import gen_info_msg
from account.models import ClickLog

ERROR_LOG = logging.getLogger('err')
CLICK_LOG = logging.getLogger('click')


class UserRestrictMiddleware(object):
    def process_request(self, request):
        """ 限制一个帐号不能不同电脑登录"""
        if request.user.is_authenticated():
            cache = get_cache('default')
            cache_timeout = 86400
            cache_key = "user_pk_%s_restrict" % request.user.pk
            cache_value = cache.get(cache_key)

            if cache_value is not None:
                if request.session.session_key != cache_value:
                    engine = import_module(settings.SESSION_ENGINE)
                    session = engine.SessionStore(session_key=cache_value)
                    session.delete()
                    cache.set(cache_key, request.session.session_key, cache_timeout)
            else:
                cache.set(cache_key, request.session.session_key, cache_timeout)


class ClickLogMiddleWare(object):
    def process_request(self, request):
        """ 用户点击纪录"""
        if request.user.is_authenticated():
            username = request.user.username
            ClickLog(
                username=username,
                click_url=request.path,
                remote_ip=request.META['REMOTE_ADDR'],
            ).save()
            CLICK_LOG.info(gen_info_msg(request, action=u'点击', url=request.path, username=username))
        else:
            ClickLog(
                username='guest',
                click_url=request.path,
                remote_ip=request.META['REMOTE_ADDR'],
            ).save()
            CLICK_LOG.info(gen_info_msg(request, action=u'点击', url=request.path, username='guest'))
