#!/usr/bin/python
# -*- coding:utf-8 -*-

from wash.models import Basket


def basket(request):
    sessionid = request.session.session_key
    total = Basket.total(sessionid)
    return {
        'total': total,
    }