#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from bookmark.models import BookMark, NotePad
from comment.models import Heart
from account.models import SpecialCare

from gather.celery import async_send_html_email

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
            if not BookMark.objects.filter(url=k).exists():
                BookMark(
                    user=request.user,
                    title=v.encode('utf-8'),
                    url=k.encode('utf-8'),
                    summary=u'无',
                ).save()
        messages.info(request, u'导入成功')       
    return render(request, template_name)


def note(request, template_name='bookmark/notes.html'):
    """ 便签显示"""
    if request.method == "POST":
        if request.user.is_authenticated():
            if request.POST.get('note'):
                title = request.POST.get('note')
                if len(title) > 45:
                    messages.error(request, 'shout out内容过长!')
                else:
                    if not NotePad.objects.filter(title=title).exists():
                        note = NotePad(
                            user=request.user,
                            title=title,
                            updated=datetime.datetime.now(),
                        )
                        note.save()
                        # 对关注者发送邮件提醒
                        interests = SpecialCare.objects.filter(care=request.user)
                        for interest in interests:
                            context = {
                                'username': note.user.username,
                                'action': '发布了新的状态:',
                                'content': note.title,
                            }
                            async_send_html_email.delay('新状态提醒', [interest.user.username,], 'new_action_template.html', context)
            else:
                messages.error(request, 'shout out不能为空')
        else:
            messages.info(request, '请登录后才能shout out')
    node_list = NotePad.objects.all().select_related().order_by("-updated")
    nodes, page_numbers = adjacent_paginator(node_list, request.GET.get('page', 1))
    return render(request, template_name, {
        'nodes': nodes,
        'pages': page_numbers,
    })
        