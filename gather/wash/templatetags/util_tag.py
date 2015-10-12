#!/usr/bin/python
# -*- coding: utf-8 -*-


from django import template


register = template.Library()

@register.filter
def dict_get(d, key):
    """How to Use

    {{ d|dict_get:key }}

    """
    return d.get(key, 0)
