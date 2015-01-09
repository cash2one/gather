#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

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
    nodes = NotePad.objects.filter(parent_id=0).order_by("-updated")
    return render(request, template_name, {
        'nodes': nodes,
    })


@csrf_exempt
def comments(request):
    """ 反馈便签中的评论信息"""
    if request.method == "POST":
        if request.is_ajax():
            note_id = request.POST.get('note_id')
            comments = []
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
            return HttpResponse(json.dumps(comments))


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



