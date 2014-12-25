#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from bookmark.models import BookMark

from soup import ParseHtml
from utils import adjacent_paginator


@login_required
def bookmark(request, template_name='bookmark/bookmark.html'):
    """ 个人书签展示"""
    bookmark_list = BookMark.objects.filter(user=request.user)
    bookmarks, bookmark_page_numbers = adjacent_paginator(bookmark_list, page=request.GET.get('page'))

    return render(request, template_name, {
        'bookmarks': bookmark_list
    })


@login_required
def import_bookmark(request, template_name='bookmark/import.html'):
    """ 导入书签"""
    if request.method == 'POST':
        book_mark = request.FILES['bookmark']
        html = ParseHtml()
        href_title = html.parse(book_mark)
        for k, v in href_title.items():
            BookMark(
                user=request.user,
                title=v.encode('utf-8'),
                url=k.encode('utf-8'),
                summary=u'无',
            ).save()
        messages.info(request, u'导入成功')
        
    return render(request, template_name)
