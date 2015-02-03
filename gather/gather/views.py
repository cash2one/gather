#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from bookmark.models import NotePad, NoteHeart

from utils import adjacent_paginator


def index(request, template_name='index.html'):
    """ 主页显示"""
    return render(request, template_name, {})


def note(request, template_name='notes.html'):
    """ 便签显示"""
    if request.method == "POST":
            if request.user.is_authenticated():
                if request.POST.get('note'):
                    title = request.POST.get('note')
                    if not NotePad.objects.filter(title=title).exists():
                        NotePad(
                            user=request.user,
                            title=title,
                            updated=datetime.datetime.now(),
                        ).save()
                else:
                    messages.error(request, 'shout out不能为空')
            else:
                messages.info(request, '请登录后才能shout out')
    node_list = NotePad.objects.filter(parent_id=0).order_by("-updated")
    nodes, page_numbers = adjacent_paginator(node_list, request.GET.get('page', 1))
    return render(request, template_name, {
        'nodes': nodes,
        'pages': page_numbers,
    })


@csrf_exempt
def comments(request):
    """ 反馈便签中的评论信息"""
    if request.method == "POST":
        if request.is_ajax():
            note_id = request.POST.get('note_id')
            note_all = {}
            comments = []
            note = NotePad.objects.get(pk=note_id)
            note.read_sum += 1
            note.save()
            level_one = NotePad.objects.filter(parent_id=note_id).order_by('created')
            level_two = NotePad.objects.filter(parent_id__in=level_one).order_by('created')
            for one in level_one:
                comment = {}
                comment['id'] = one.id
                comment['comment'] = one.comment
                comment['username'] = one.user.username
                comment['created'] = str(one.created)[:20]
                try:
                    big_photo = one.user.profile.big_photo.url
                except:
                    big_photo = '/static/images/default_head.png'
                comment['url'] = big_photo
                for two in level_two:
                    reply = {}
                    if two.parent_id == one.id:
                        reply['id'] = two.id
                        reply['comment'] = two.comment
                        reply['created'] = str(two.created)[:20]
                        try:
                            big_photo = two.user.profile.big_photo.url
                        except:
                            big_photo = '/static/images/default_head.png'
                        reply['url'] = big_photo
                        try:
                            comment['replys']
                        except KeyError:
                            comment['replys'] = []
                        comment['replys'].append(reply)
                comments.append(comment)
            note_all = {
                'id': note_id,
                'title': note.title,
                'read_sum': note.read_sum,
                'heart': NoteHeart.objects.filter(note=note, is_still=True).count(),
                'created': str(note.created)[:20],
                'username': note.user.username,
                'comments': comments,
            }
            return HttpResponse(json.dumps(note_all))


@csrf_exempt
def add_comment(request):
    """ 便签添加评论"""
    if request.method == 'POST':
        if request.user.is_authenticated():
            if request.is_ajax():
                comment = request.POST.get('comment')
                note_id = request.POST.get('note_id')
                note = NotePad.objects.get(pk=note_id)
                c = NotePad(
                    user=request.user,
                    comment=comment,
                    parent_id=note_id,
                    updated=datetime.datetime.now(),
                )
                c.save()
                note.updated = datetime.datetime.now()
                note.save()
                try:
                    big_photo = c.user.profile.big_photo.url
                except:
                    big_photo = '/static/images/default_head.png'
                comment_json = {
                    'comment': c.comment,
                    'id': c.id,
                    'created': str(c.created)[:20],
                    'username': c.user.username,
                    'url': big_photo,
                }
                return HttpResponse(json.dumps(comment_json))
        else:
            return HttpResponse(json.dumps(False))


@require_POST
@csrf_exempt
def heart(request):
    """ 喜欢"""
    if request.user.is_authenticated():
        if request.is_ajax():
            user = request.user
            note_id = request.POST.get('note_id')
            note = NotePad.objects.get(pk=note_id)
            try:
                # 已经喜欢, 取消喜欢
                heart = NoteHeart.objects.get(note=note, user=user, is_still=True)
                heart.is_still = False
                heart.save()
                data = {
                    'result': True,
                    'sign': False,
                }
                return HttpResponse(json.dumps(data))
            except NoteHeart.DoesNotExist:
                # 添加喜欢
                NoteHeart(
                    user=user,
                    note=note,
                    is_still=True,
                ).save()
                data = {
                    'result': True,
                    'sign': True,
                }
                return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(json.dumps({'result': False}))




