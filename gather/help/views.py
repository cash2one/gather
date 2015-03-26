#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def help(request, template_name='help/index.html'):
    """ 地图展示"""
    return render(request, template_name, {
    })
