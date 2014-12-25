#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render


def bookmark(request, template_name='bookmark/bookmark.html'):
    """ 个人书签展示"""
    return render(request, template_name)


def import_bookmark(request, template_name='bookmark/import.html'):
    """ 导入书签"""
    print request.FILES
    return render(request, template_name)
