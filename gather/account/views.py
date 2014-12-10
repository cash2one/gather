#!/usr/bin/python
#-*- coding: utf-8 -*-

import base64

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.signing import Signer, TimestampSigner, SignatureExpired, BadSignature
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render

from account.forms import RegistForm
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


def login(request, form_class, tempalte_name='account/login.html'):
    """ 用户登录"""
    return render(request, tempalte_name)


def regist(request, form_class, tempalte_name='account/regist.html'):
    """ 用户注册"""
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            form.save()

    else:
        form = form_class()
    return render(request, tempalte_name, {
        'form': form,
    })
