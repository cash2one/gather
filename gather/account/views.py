#!/usr/bin/python
#-*- coding: utf-8 -*-

import base64

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.core.signing import Signer, TimestampSigner, SignatureExpired, BadSignature
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render

from smtplib import SMTPRecipientsRefused

from account.forms import RegistForm, LoginForm
from account.models import UserProfile

def send_verify_email(request, title, email, url, template_name, **kwargs):
    """ 发送验证邮件"""
    signer = TimestampSigner()
    verify_code = base64.b64encode(signer.sign(email))
    verify_url = 'http://' + request.META['HTTP_HOST'] + '/account/' + url + '/?code=' + verify_code
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


def login(request, form_class=LoginForm, template_name='account/login.html'):
    """ 用户登录"""
    return render(request, template_name)


def regist(request, form_class=RegistForm, template_name='account/email_verify.html'):
    """ 用户注册"""
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            profile = form.save()
            title = u'Gather 注册邮件'
            url = 'verify'
            template_name = 'account/email_verify_template.html'
            index = profile.email.index('@')
            email_site = 'http://mail.' + profile.email[index + 1:]
            result = send_verify_email(request, title, profile.username, url, template_name)
            if result:
                return render(request, 'account/email_verify.html', {
                    'mask_email': profile.get_mask_email(),
                    'email_site': email_site,
                })
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form,
    })


def email_verify(request, template_name='account/email_verify_succ.html'):
    """ 验证邮箱"""
    return render(request, template_name)


def resend_bind_email(request, template_name='account/email_verify.html'):
    """ 重新发送验证邮件"""
    code = request.GET.get('code', None)
    title = u'Gather 注册邮件'
    url = 'verify'
    template_name = 'account/email_verify_template.html'
    index = profile.email.index('@')
    email_site = 'http://mail.' + profile.email[index + 1:]
    result = send_verify_email(request, title, profile.username, url, template_name)
    return render(request, 'account/email_verify.html', {
            'mask_email': profile.get_mask_email(),
            'email_site': email_site,
        })
