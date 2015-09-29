#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import login, authenticate

from wash.models import WashType
from account.models import LoginLog
from wash.forms import RegistForm, WashTypeForm
from CCPRestSDK import REST
from utils import gen_verify_code


def manage_login(request, template_name="wash/manage/login.html"):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                user = authenticate(username=username, password=password)
                login(request, user)
                LoginLog(
                    username=username,
                    login_ip=request.META['REMOTE_ADDR'],
                    is_succ=True,
                ).save()
                return HttpResponseRedirect(reverse("wash.mviews.manage_index"))
            else:
                messages.error(request, u"密码错误")
        except User.DoesNotExist:
            messages.error(request, u"用户不存在")
    return render(request, template_name)


@login_required(login_url='/wash/manage/')
def manage_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, u'已成功退出')
    return HttpResponseRedirect(reverse("wash.mviews.manage_login"))


@login_required(login_url='/wash/manage/')
def manage_index(request, template_name="wash/manage/base.html"):
    return render(request, template_name)


@login_required(login_url='/wash/manage/')
def wash_type(request, template_name="wash/manage/wash_type.html"):
    """
    洗刷类型清单
    :param request:
    :param template_name:
    :return:
    """
    wash_types = WashType.objects.all()
    return render(request, template_name, {
        'wash_types': wash_types
    })


@login_required(login_url='/wash/manage/')
def wash_type_add(request, form_class=WashTypeForm, template_name="wash/manage/wash_type_add.html"):
    """
    洗刷类型添加
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        form = form_class(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
    form = form_class()
    return render(request, template_name, {
        'measures': WashType.MEASURE,
        'belongs': WashType.WASH_TYPE,
        'form': form,
    })


@login_required(login_url='/wash/manage/')
def wash_type_update(request, type_id, template_name="wash/manage/wash_type_add.html"):
    """
    洗刷类型添加
    :param request:
    :param template_name:
    :return:
    """
    try:
        wash_type = WashType.objects.get(id=type_id)
        messages.info(request, u"修改成功")

    except WashType.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse("wash.mviews.wash_type"))
