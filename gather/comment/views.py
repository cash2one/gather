#!/usr/bin/python
#-*- coding: utf-8 -*-

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

from comment.models import Heart, NoteComment, ShareComment, HelpComment
from account.models import SpecialCare
from bookmark.models import NotePad
from help.models import Help
from share.models import Share

from gather.celery import async_send_html_email


@csrf_exempt
def comments(request, obj_type=None, obj_id=None):
    """ 反馈评论信息"""
    obj_modal = get_modal(obj_type)    
    comment_modal = get_comment_modal(obj_type)

    if request.method == "GET":
        if request.is_ajax():
            note_all = {}
            comments = []
            with transaction.atomic():
                obj = obj_modal.objects.select_for_update().get(pk=obj_id)
                obj.read_sum += 1
                obj.save()

            level_one = comment_modal.objects.filter(parent_obj_id=obj_id, parent_comment_id=0).order_by('created')
            level_two = comment_modal.objects.filter(parent_comment_id__in=level_one).order_by('created')
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
                    if two.parent_comment_id == one.id:
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
                comments.append(comment);
            # 未登录处理
            try:
                profile = request.user.profile
                is_heart = Heart.objects.filter(heart_id=obj_id, is_still=True, user=request.user).exists()
            except:
                profile = None
                is_heart = False
            note_all = {
                'id': obj_id,
                'user_id': obj.user.id,
                'special_care': profile.is_special_care(obj.user) if profile else False,
                'is_self_action': profile.is_self_action(obj_modal, obj_id) if profile else True,
                'title': obj.title,
                'read_sum': obj.read_sum,
                'heart_num': Heart.objects.filter(heart_id=obj_id, is_still=True).count(),
                'is_heart': is_heart,
                'created': str(obj.created)[:20],
                'username': obj.user.username,
                'comments': comments,
                'url': obj.user.profile.get_owner_photo(),
            }
            return HttpResponse(json.dumps(note_all))
    return HttpResponse(json.dumps({'result': False, 'msg': ''}))


@csrf_exempt
def add_comment(request, obj_type):
    """ 便签添加评论"""
    obj_modal = get_modal(obj_type)
    comment_modal = get_comment_modal(obj_type)

    if request.method == 'POST':
        owner = request.user
        if request.user.is_authenticated():
            if request.is_ajax():
                comment = request.POST.get('comment')
                obj_id = request.POST.get('obj_id')
                parent_id = request.POST.get('parent_id')
                comment_type = request.POST.get('comment_type')
                obj = obj_modal.objects.get(pk=obj_id)
                # 回复评论中的评论
                if comment_type == 'answer':
                    reply = request.POST.get('reply')
                    replyer = User.objects.get(username=reply)
                    c = comment_modal(
                        user=request.user,
                        comment=comment,
                        parent_comment_id=parent_id,
                        parent_obj_id=obj_id,
                        reply_to=replyer,
                    )
                    # 二级评论提醒, 状态所有者和被回复者被提醒
                    if replyer.username != owner.username and replyer.username != obj.user.username:
                        context = {
                            'username': owner.username,
                            'action': '回复了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', owner.username, 'new_action_template.html', context)
                        context = {
                            'username': obj.user.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', obj.user.username, 'new_action_template.html', context)

                    elif replyer.username == owner.username and replyer.username != obj.user.username:
                        context = {
                            'username': obj.user.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', obj.user.username, 'new_action_template.html', context)

                    elif replyer.username != owner.username and replyer.username == obj.user.username:
                        context = {
                            'username': owner.username,
                            'action': '评论了您的状态:',
                            'content': c.comment,
                        }
                        async_send_html_email.delay('新状态提醒', owner.username, 'new_action_template.html', context)
                else:
                    c = comment_modal(
                        user=owner,
                        comment=comment,
                        parent_obj_id=obj_id,
                    )
                c.save()
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
                    'parent_id': obj.id,
                    'result': True,
                }
                # 一级评论提醒, 状态所有者被提醒
                if owner.username != obj.user.username:
                    context = {
                        'username': owner.username,
                        'action': '评论了您的状态:',
                        'content': c.comment,
                    }
                    async_send_html_email.delay('新状态提醒', [obj.user.username,], 'new_action_template.html', context)
            return HttpResponse(json.dumps(comment_json))
    return HttpResponse(json.dumps({'result': False, 'msg': '请登录'}))


@require_POST
@csrf_exempt
def heart(request, obj_type=None, obj_id=None):
    """ 喜欢"""
    obj_modal = get_modal(obj_type)

    if request.user.is_authenticated():
        if request.is_ajax():
            user = request.user
            obj = obj_modal.objects.get(id=obj_id)
            try:
                # 已经喜欢, 取消喜欢
                with transaction.atomic():
                    heart = Heart.objects.select_for_update().get(heart_id=obj_id, user=user, heart_type=obj_type, is_still=True)
                    heart.is_still = False
                    heart.save()
                    data = {
                        'result': True,
                        'sign': False,
                    }
                    return HttpResponse(json.dumps(data))
            except Heart.DoesNotExist:
                # 添加喜欢
                Heart(
                    user=user,
                    heart_id=obj_id,
                    heart_type=obj_type,
                    is_still=True,
                ).save()
                data = {
                    'result': True,
                    'sign': True,
                }
                context = {
                    'username': user.username,
                    'action': '赞了您的状态:',
                    'content': obj.title,
                }
                if request.user.username != obj.user.username:
                    async_send_html_email.delay('新状态提醒', [obj.user.username,], 'new_action_template.html', context)
                return HttpResponse(json.dumps(data))
    return HttpResponse(json.dumps({'result': False, 'msg': '请登录'}))


@csrf_exempt
def special_care(request, user_id=None):
    """ 特别关心"""
    if request.user.is_authenticated:
        if request.is_ajax() and request.method == "POST":
            care_type = request.POST.get('care_type', None)
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


def get_modal(obj_type):
    """ 获取Modal"""
    obj_modal = None
    if obj_type == 'share':
        obj_modal = Share
    elif obj_type == 'help':
        obj_modal = Help
    elif obj_type == 'note':
        obj_modal = NotePad
    return obj_modal


def get_comment_modal(obj_type):
    """ 获取Comment_Modal"""
    obj_modal = None
    if obj_type == 'share':
        obj_modal = ShareComment
    elif obj_type == 'help':
        obj_modal = HelpComment
    elif obj_type == 'note':
        obj_modal = NoteComment
    return obj_modal
