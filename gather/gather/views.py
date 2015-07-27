#!/usr/bin/python
#-*- coding: utf-8 -*-

from django.shortcuts import render

from config.models import DevelopLog


def index(request, template_name='index.html'):
    """ 主页显示"""
    return render(request, template_name, {})


def about_us(request, template_name='about_us.html'):
    """ 关于我"""
    logs = DevelopLog.objects.all().order_by('-created')
    return render(request, template_name, {
        'logs': logs
    })
