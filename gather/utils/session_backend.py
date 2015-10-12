#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.sessions.backends.db import SessionStore as DbSessionStore

# 防止登陆后sessionid重置
class SessionStore(DbSessionStore):
    def cycle_key(self):
        pass