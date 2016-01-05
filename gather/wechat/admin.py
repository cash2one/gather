#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from wechat.models import *


admin.site.register(WeToken)
admin.site.register(WeJsapi)
admin.site.register(WeProfile)
