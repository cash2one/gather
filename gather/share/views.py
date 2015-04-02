#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from share.forms import ShareForm
from share.models import Share

from utils import adjacent_paginator


def share(request, template_name='share/share_list.html'):
    """ 分享展示"""
    share_list = Share.objects.all().order_by("-updated")
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
            form.save()
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
    except Share.DoesNotExist:
        return HttpResponseRedirect(reverse('share.views.share'))

    return render(request, template_name, {
        'share': share,
    })
