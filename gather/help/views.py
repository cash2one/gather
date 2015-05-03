#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson as json

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from help.forms import AddHelpForm
from help.models import Help


def help(request, template_name='help/index.html'):
    """ 地图展示"""
    return render(request, template_name, {
    })


@login_required
def help_add(request, form_class=AddHelpForm, template_name='help/index.html'):
    """ 添加帮助"""
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            help = form.save()
            return render(request, template_name, {
                'latitude': help.latitude,
                'longitude': help.longitude,
                'new_help_show': True,
            })

    return HttpResponseRedirect(reverse('help.views.help'))


def help_points(request):
    """ 获取所有有效的需要帮助的点"""
    if request.is_ajax():
        helps = Help.objects.filter(is_valid=True)
        points = []
        for help in helps:
            points.append([help.longitude, help.latitude, help.id])
        data = {
            'result': True,
            'points': points,
        }
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(json.dumps({'result': False}))


def help_detail(request, help_id=None):
    """ 获取一个拜托信息的详细内容"""
    if request.is_ajax():
        try:
            help = Help.objects.get(pk=help_id)
            data = {
                'result': True,
                'id': help.id,
                'latitude': help.latitude,
                'longitude': help.longitude,
                'connect_method': help.connect_method,
                'title': help.title,
                'content': help.content,
                'remark': help.remark,
                'cancel_time': str(help.cancel_time)[:20],
                'username': help.seeker.username,
                'is_self': help.is_self(request.user),
            }
            return HttpResponse(json.dumps(data))
        except Help.DoesNotExist:
            return HttpResponse(json.dumps({'result': False}))


def help_list(request):
    """ 获取一个坐标上的所有拜托信息"""
    if request.is_ajax():
        try:
            x = request.GET.get('x')
            y = request.GET.get('y')
            count = Help.objects.filter(longitude=x, latitude=y).count()
            if count == 1:
                help = Help.objects.get(longitude=x, latitude=y)
                data = {
                    'result': True,
                    'id': help.id,
                    'latitude': help.latitude,
                    'longitude': help.longitude,
                    'connect_method': help.connect_method,
                    'title': help.title,
                    'content': help.content,
                    'remark': help.remark,
                    'cancel_time': str(help.cancel_time)[:20],
                    'username': help.seeker.username,
                    'is_self': help.is_self(request.user),
                    'is_single': True,
                }
            else:
                help_list = Help.objects.filter(longitude=x, latitude=y)
                helps = []
                for help in help_list:
                    help_detail = {
                        'id': help.id,
                        'latitude': help.latitude,
                        'longitude': help.longitude,
                        'connect_method': help.connect_method,
                        'title': help.title,
                        'content': help.content,
                        'remark': help.remark,
                        'cancel_time': str(help.cancel_time)[:20],
                        'username': help.seeker.username,
                        'is_self': help.is_self(request.user),
                    }
                    helps.append(help_detail)
                data = {
                    'result': True,
                    'helps': helps,
                    'is_single': False,
                }
            return HttpResponse(json.dumps(data))
        except Help.DoesNotExist:
            return HttpResponse(json.dumps({'result': False}))
