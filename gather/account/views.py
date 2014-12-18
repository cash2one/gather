#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render

from smtplib import SMTPRecipientsRefused

from account.forms import RegistForm, LoginForm

from config.decorators import code_valid, unlogin_required
from utils import get_decipher_username, get_encrypt_code


def send_verify_email(request, title, email, url, template_name, **kwargs):
    """ 发送验证邮件"""
    code = get_encrypt_code(email)
    verify_url = 'http://' + request.META['HTTP_HOST'] + '/account/' + url + '/?code=' + code
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
                return HttpResponseRedirect(reverse('gather.views.index'))
            else:
                code = get_encrypt_code(user.username)
                return HttpResponseRedirect('%s?code=%s' % (reverse('account.views.send_bind_email'), code))
    else:
        form = form_class()
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


def account(request, template_name="account/index.html"):
    """ 个人账户页"""
    return render(request, template_name)


def logout(request):
    """ 退出登录"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, '已成功退出')
    return HttpResponseRedirect('/')
