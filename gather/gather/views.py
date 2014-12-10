#!/usr/bin/python
#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


def index(request, template_name='index.html'):
    """ 主页显示"""
    return render(request, template_name)
