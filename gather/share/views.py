#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from share.forms import ShareForm
from share.models import Share

from utils import adjacent_paginator


def share(request, template_name='share/share_list.html'):
    """ 分享展示"""
    share_list = Share.objects.exclude(content='').order_by("-created")
    shares, page_numbers = adjacent_paginator(share_list, request.GET.get('page', 1), page_num=10)
    
    return render(request, template_name, {
        'shares': shares,
        'page_numbers': page_numbers,
    })


@login_required
def add_share(request, form_class=ShareForm, template_name='share/add_share.html'):
    """ 分享"""
    if request.method == "POST":
        form = form_class(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            share = form.save()
            if share.content == '':
                return HttpResponseRedirect(reverse("share.views.photo_share"))
            else:
                return HttpResponseRedirect(reverse("share.views.share"))
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
    })


def detail_share(request, share_id, template_name='share/detail_share.html'):
    """ 分享内容展示"""
    try:
        share = Share.objects.get(id=share_id)
        with transaction.atomic():
            share.read_sum += 1
            share.save()
    except Share.DoesNotExist:
        return HttpResponseRedirect(reverse('share.views.share'))

    return render(request, template_name, {
        'share': share,
    })


def photo_share(request, template_name='share/photo_wall.html'):
    """ 照片墙"""
    #walls = get_photo_share(request)
    walls = Share.objects.exclude(photo='').order_by('-created')

    return render(request, template_name, {
        'walls': walls,
        'page_num': 2
    })


def photo_share_more(request):
    """ 点击获取更多照片墙"""
    if request.is_ajax():
        walls = get_photo_share(request)
        results = {}
        if walls:
            data = []
            for wall in walls:
                _data = {}
                _data['photo'] = wall.photo.name
                _data['title'] = wall.title
                _data['xsize'] = wall.xsize
                _data['ysize'] = wall.ysize
                data.append(_data)
            results['data'] = data
            results['result'] = True
            results['msg'] = 'success'
            results['page_num'] = int(request.GET.get('page', 1)) + 1
        else:
            results['result'] = False
            results['msg'] = u'没有更多了'

    return HttpResponse(json.dumps(results))


def get_photo_share(request):
    page_size = 6
    page_num = int(request.GET.get('page', 1))
    page_start = page_size * (page_num - 1)
    page_end = page_start + page_size
    print page_start, page_end
    walls = Share.objects.filter(content='')[page_start:page_end]
    return walls
