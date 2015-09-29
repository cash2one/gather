#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import login, authenticate

from wash.models import VerifyCode, WashUserProfile
from wash.forms import RegistForm
from CCPRestSDK import REST
from utils import gen_verify_code


def auto_login(func):
    def wrapped(_request, *args, **kwargs):
        user = _request.user
        if not user.is_authenticated():
            if WashUserProfile.user_valid(user):
                user = authenticate(remote_user=user.username)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(_request, user)
            else:
                return HttpResponseRedirect((reverse('wash.views.regist')))
        return func(_request, *args, **kwargs)
        wrapped.__doc__ = func.__doc__
        wrapped.__name__ = func.__name__
    return wrapped


def index(request, template_name='wash/index.html'):
    return render(request, template_name)


def show(request, template_name='wash/show.html'):
    return render(request, template_name)


def regist(request, form_class=RegistForm, template_name='wash/regist.html'):
    if request.method == "POST":
        form = form_class(data=request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('wash.views.index'))
    else:
        form = form_class()
    return render(request, template_name, {
        'form': form
    })


@csrf_exempt
def verify_code(request):
    if request.is_ajax():
        phone = request.POST.get('phone', '')
        if len(phone) == 11:
            if WashUserProfile.objects.filter(phone=phone, is_phone_verified=True).exists():
                return reverse('wash.views.index')
            else:
                rest = REST()
                if VerifyCode.objects.filter(phone=phone, is_expire=False).exists():
                    verify = VerifyCode.objects.get(phone=phone, is_expire=False)
                    if (datetime.datetime.today() - verify.created).seconds > settings.VERIFY_CODE_EXPIRE:
                        verify_code = gen_verify_code()
                        verify.is_expire = True
                        verify.save()
                        VerifyCode(phone=phone, code=verify_code).save()
                    else:
                        verify_code = verify.code
                else:
                    verify_code = gen_verify_code()
                    VerifyCode(phone=phone, code=verify_code).save()
                result = rest.voice_verify(verify_code, phone)
                return HttpResponse(json.dumps({'result': result}))
        return HttpResponse(json.dumps({"result": False, 'msg': u'手机号格式错误'}))
    return render(request)


@auto_login
def account(request, template_name='wash/account.html'):
    user = request.user
    profile = WashUserProfile.objects.get(user=user)
    return render(request, template_name, {
        'profile', profile
    })





