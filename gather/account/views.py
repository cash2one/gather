#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime
import logging
import simplejson as json

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render

from smtplib import SMTPRecipientsRefused

from account.forms import RegistForm, LoginForm, UploadBigPicForm
from bookmark.models import NotePad
from share.models import Share

from config.decorators import code_valid, unlogin_required
from utils import get_decipher_username, get_encrypt_code, gen_info_msg, resize_avatar, crop_avatar

INFO_LOG = logging.getLogger('info')
LOGIN_LOG = logging.getLogger('login')


def send_verify_email(request, title, email, url, template_name, **kwargs):
    """ 发送验证邮件"""
    code = get_encrypt_code(email)
    # verify_url = 'http://' + request.META['HTTP_HOST'] + '/account/' + url + '/?code=' + code
    verify_url = 'http://www.jacsice.cn/account/' + url + '/?code=' + code
    context = {
        'nickname': email,
        'verify_url': verify_url,
    }
    context.update(kwargs)
    t = loader.get_template(template_name)
    mail_list = [email, ]
    try:
        msg = EmailMultiAlternatives(title, t.render(Context(context)), settings.DEFAULT_FROM_EMAIL, mail_list)
        msg.content_subtype = 'html'
        msg.send()
        return True
    except SMTPRecipientsRefused:
        messages.error(request, '邮箱不存在，请换个邮箱')
        return False


@unlogin_required
def login(request, form_class=LoginForm, template_name='index.html'):
    """ 用户登录"""
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.POST.get('username'))
            if user.is_active:
                form.login()
                next = request.GET.get('next', '/')
                return HttpResponseRedirect(next)
            else:
                code = get_encrypt_code(user.username)
                LOGIN_LOG.info(gen_info_msg(request, action=u'未验证用户登陆'))
                return HttpResponseRedirect('%s?code=%s' % (reverse('account.views.send_bind_email'), code))
    else:
        form = form_class(request)
    return render(request, template_name, {
        'form': form,
    })


@unlogin_required
def regist(request, form_class=RegistForm, template_name='account/regist.html'):
    """ 用户注册"""
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            profile = form.save()
            code = get_encrypt_code(profile.username)
            title = u'Gather 注册邮件'
            url = 'verify'
            verify_template_name = 'account/email_verify_template.html'
            username = profile.username
            INFO_LOG.info(gen_info_msg(request, action=u'发送验证邮件', user_id=request.user.id))
            send_verify_email(request, title, username, url, verify_template_name)
            return HttpResponseRedirect('%s?code=%s' % (reverse('account.views.send_bind_email'), code))
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
    })


@code_valid
@unlogin_required
def send_bind_email(request, template_name='account/email_verify_succ.html'):
    """ 发送验证邮箱"""
    code = request.GET.get('code', None)
    username = get_decipher_username(request)
    index = username.index('@')
    email_site = 'http://mail.' + username[index + 1:]
    email_mask = username[:3] + "******" + '.com'
    return render(request, 'account/email_verify.html', {
        'email_mask': email_mask,
        'email_site': email_site,
        'code': code,
    })
    return render(request, template_name)


@code_valid
@unlogin_required
def verify(request, template_name='account/email_verify_succ.html'):
    """ 验证邮箱"""
    username = get_decipher_username(request)
    if User.objects.filter(username=username, is_active=True).exists():
        messages.error(request, '您已注册成功, 请登录!')
        return HttpResponseRedirect(reverse('gather.views.index'))
    else:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        profile = user.profile
        profile.is_mail_verified = True
        profile.mail_verified_date = datetime.datetime.now()
        profile.save()
        INFO_LOG.info(gen_info_msg(request, action=u'验证邮件成功', user_id=request.user.id))
        return render(request, template_name, {
            'email_mask': username[:3] + "******" + '.com'
        })


@code_valid
@unlogin_required
def resend_bind_email(request, template_name='account/email_verify.html'):
    """ 重新发送验证邮箱的邮件"""
    code = request.GET.get('code', None)
    username = get_decipher_username(request)
    if User.objects.filter(username=username, is_active=True).exists():
        messages.error(request, '您已注册成功, 请登录!')
        return HttpResponseRedirect(reverse('gather.views.index'))
    else:
        title = u'Gather 注册邮件'
        url = 'verify'
        verify_template_name = 'account/email_verify_template.html'
        index = username.index('@')
        email_site = 'http://mail.' + username[index + 1:]
        email_mask = username[:3] + "******" + '.com'
        send_verify_email(request, title, username, url, verify_template_name)
        return render(request, template_name, {
            'email_mask': email_mask,
            'email_site': email_site,
            'code': code,
        })


@login_required
def account(request, template_name="account/index.html"):
    """ 个人账户页"""
    shouts = NotePad.objects.filter(user=request.user).order_by('-created')
    return render(request, template_name, {
        'shouts': shouts,
    })


@login_required
def article(request, template_name="account/articles.html"):
    """ 我的文章"""
    shares = Share.objects.filter(user=request.user)
    return render(request, template_name, {
        'shares': shares,
    })


@login_required
def add_article(request, template_name="account/add_article.html"):
    """ 添加文章"""
    return render(request, template_name)


@csrf_exempt
@login_required
def head_pic_big(request, form_class=UploadBigPicForm, template_name='account/upload_pic.html'):
    """ 上传大头像"""
    profile = request.user.profile

    if request.method == 'POST':
        crop = request.POST.get('crop')
        if crop == '':
            form = form_class(data=request.POST, files=request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                resize_avatar(request, profile)
        else:
            crop_avatar(request, profile)
            form = form_class()
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
        'profile': profile,
    })


@login_required
def logout(request):
    """ 退出登录"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, '已成功退出')
    next = request.GET.get('next', '/')
    return HttpResponseRedirect(next)
