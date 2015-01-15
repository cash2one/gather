#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import get_cache
from django.utils.importlib import import_module

ERROR_LOG = logging.getLogger('err')


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
