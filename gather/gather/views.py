#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from bookmark.models import NotePad, NoteHeart, SpecialCare

from utils import adjacent_paginator
from gather.celery import async_send_html_email

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
    node_list = NotePad.objects.filter(parent_id=0).select_related().order_by("-updated")
    nodes, page_numbers = adjacent_paginator(node_list, request.GET.get('page', 1))
    return render(request, template_name, {
        'nodes': nodes,
        'pages': page_numbers,
    })


@csrf_exempt
def comments(request, note_id=None):
    """ 反馈便签中的评论信息"""
    if request.method == "GET":
        if request.is_ajax():
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
                comment['replys'] = []
                for two in level_two:
                    reply = {}
                    if two.parent_id == one.id:
                        reply['id'] = two.id
                        reply['comment'] = two.comment
                        reply['username'] = two.user.username
                        reply['created'] = str(two.created)[:20]
                        if two.user.username != two.reply_to.username:
                            reply['reply_to'] = two.reply_to.username
                        else:
                            # 自己回复自己的评论不显示被回复者
                            reply['reply_to'] = ''
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
                'user_id': note.user.id,
                'special_care': note.is_special_care(request.user),
                'is_self_note': note.is_self_note(request.user),
                'title': note.title,
                'read_sum': note.read_sum,
                'heart': NoteHeart.objects.filter(note=note, is_still=True).count(),
                'created': str(note.created)[:20],
                'username': note.user.username,
                'comments': comments,
                'url': note.get_owner_photo(),
            }
            return HttpResponse(json.dumps(note_all))
    return HttpResponse(json.dumps({'result': False, 'msg': ''}))


@csrf_exempt
def add_comment(request):
    """ 便签添加评论"""
    if request.method == 'POST':
        owner = request.user
        if request.user.is_authenticated():
            if request.is_ajax():
                comment = request.POST.get('comment')
                note_id = request.POST.get('note_id')
                parent_id = request.POST.get('parent_id')
                comment_type = request.POST.get('comment_type')
                note = NotePad.objects.get(pk=note_id)
                # 回复评论中的评论
                if comment_type == 'answer':
                    reply = request.POST.get('reply')
                    replyer = User.objects.get(username=reply)
                    c = NotePad(
                        user=request.user,
                        comment=comment,
                        parent_id=parent_id,
                        parent_note_id=note_id,
                        reply_to=replyer,
                        updated=datetime.datetime.now(),
                    )
                    # 二级评论提醒, 状态所有者和被回复者被提醒
                    if replyer.username != owner.username and replyer.username != note.user.username:
                        context = {
                            'username': owner.username,
                            'action': '回复了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', owner.username, 'new_action_template.html', context)
                        context = {
                            'username': note.user.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', note.user.username, 'new_action_template.html', context)

                    elif replyer.username == owner.username and replyer.username != note.user.username:
                        context = {
                            'username': note.user.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', note.user.username, 'new_action_template.html', context)

                    elif replyer.username != owner.username and replyer.username == note.user.username:
                        context = {
                            'username': owner.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', owner.username, 'new_action_template.html', context)
                else:
                    c = NotePad(
                        user=owner,
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
                    'result': True,
                }
                # 一级评论提醒, 状态所有者被提醒
                if owner.username != note.user.username:
                    context = {
                        'username': owner.username,
                        'action': '评论了您的状态:',
                        'content': c.comment,
                    }
                    async_send_html_email.delay('新状态提醒', [note.user.username,], 'new_action_template.html', context)
                # 对关注者发送邮件提醒
                interests = SpecialCare.objects.filter(care=note.user)
                for interest in interests:
                    context = {
                        'username': note.user.username,
                        'action': '发布了新的状态:',
                        'content': note.comment,
                    }
                    async_send_html_email.delay('新状态提醒', [interest.user.username,], 'new_action_template.html', context)
                
                return HttpResponse(json.dumps(comment_json))
    return HttpResponse(json.dumps({'result': False, 'msg': '请登录'}))


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
                with transaction.atomic():
                    heart = NoteHeart.objects.select_for_update().get(note=note, user=user, is_still=True)
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
                context = {
                    'username': user.username,
                    'action': '赞了您的状态:',
                    'content': note.title,
                }
                if request.user.username != note.user.username:
                    async_send_html_email.delay('新状态提醒', [note.user.username,], 'new_action_template.html', context)
                return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps({'result': False, 'msg': '请登录'}))


@csrf_exempt
def special_care(request):
    """ 特别关心"""
    if request.user.is_authenticated:
        if request.is_ajax() and request.method == "POST":
            care_type = request.POST.get('care_type', None)
            user_id = request.POST.get('user_id', None)
            # 自己不能关注自己
            if user_id != request.user.id:
                try:
                    care = User.objects.get(id=user_id)
                    if care_type == 'care':
                        with transaction.atomic():
                            if SpecialCare.objects.filter(user=request.user, care=care, is_valid=False).exists():
                                special = SpecialCare.objects.select_for_update().get(user=request.user, care=care, is_valid=False)
                                special.is_valid = True
                                special.save()
                            else:
                                SpecialCare(
                                    user=request.user,
                                    care=care,
                                    is_valid=True,
                                ).save()
                        return HttpResponse(json.dumps({'result': True, 'msg': '已关注', 'action': 'care'}))
                    elif care_type == 'cancel':
                        with transaction.atomic():
                            special = SpecialCare.objects.select_for_update().get(user=request.user, care=care, is_valid=True)
                            special.is_valid = False
                            special.save()
                            return HttpResponse(json.dumps({'result': True, 'msg': '已取消', 'action': 'cancel'}))
                except User.DoesNotExist:
                    return HttpResponse(json.dumps({'result': False, 'msg': '用户不存在'}))
                except SpecialCare.DoesNotExist:
                    return HttpResponse(json.dumps({'result': False, 'msg': '用户未特别关心'}))
    return HttpResponse(json.dumps({'result': False, 'msg': '请登录'}))

        