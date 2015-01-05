#!/usr/bin/python
#-*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from bookmark.models import NotePad

from config.models import IndexImg, IndexText
from config.decorators import click_log


@click_log
def index(request, template_name='index.html'):
    """ 主页显示"""
    if request.method == "POST":
        if request.user.is_authenticated():
            if request.POST.get('note'):
                title = request.POST.get('note')
                if not NotePad.objects.filter(title=title).exists():
                    NotePad(
                        user=request.user,
                        title=title,
                    ).save()
            else:
                messages.error(request, 'shout out不能为空')

        else:
            messages.info(request, '请登录后才能shout out')
    nodes = NotePad.objects.all().order_by("created")
    return render(request, template_name, {
        'nodes': nodes,
    })
