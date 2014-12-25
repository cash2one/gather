#!/usr/bin/python
#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from config.models import IndexImg, IndexText
from config.decorators import click_log


@click_log
def index(request, template_name='index.html'):
    """ 主页显示"""
    imgs = IndexImg.objects.filter(is_show=True).order_by('ordering')[:1]
    texts = IndexText.objects.filter(is_show=True)[:1]
    return render(request, template_name, {
        'imgs': imgs,
        'texts': texts,
    })
