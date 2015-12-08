#!/usr/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal, getcontext

from django import template


register = template.Library()

@register.filter
def dict_get(d, key):
    """How to Use

    {{ d|dict_get:key }}

    """
    return d.get(key, 0)


@register.filter
def money_format(value):
    """ 分转换为元"""
    try:
        value = str(int(value) / 100.00)
        return '{0:,}'.format(Decimal(value.rstrip('0').rstrip('.')))
    except (ValueError, TypeError):
        return value
