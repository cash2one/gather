#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from wash.models import *


admin.site.register(Company)
admin.site.register(WashUserProfile)
admin.site.register(Address)
admin.site.register(IndexBanner)
admin.site.register(WeToken)
admin.site.register(VerifyCode)
admin.site.register(UserAddress)
admin.site.register(WashType)
admin.site.register(Discount)
admin.site.register(MyDiscount)
admin.site.register(Basket)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(OrderLog)
admin.site.register(PayRecord)
admin.site.register(Advice)
admin.site.register(Config)
