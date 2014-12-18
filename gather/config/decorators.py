#!/usr/bin/python
# -*- coding:utf-8 -*-

import base64

from django.conf import settings
from django.contrib import messages
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from functools import wraps

ONE_DAY = 24 * 60 * 60


def code_valid(func):
    """ 检验code的准确性"""
    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        if request.method == "POST":
            code = request.POST.get('code', None)
            if code is None:
                code = request.GET.get('code', None)
        else:
            code = request.GET.get('code', None)
        if code:
            try:
                value = base64.b64decode(code)
                signer = TimestampSigner()
                signer.unsign(value, ONE_DAY)
                return func(request, *args, **kwargs)
            except (SignatureExpired, BadSignature, TypeError), e:
                if isinstance(e, SignatureExpired):
                    messages.error(request, '链接已失效')
                elif isinstance(e, BadSignature):
                    messages.error(request, '链接被篡改')
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    return returned_wrapper


def unlogin_required(func):
    """ 不允许登录用户进入"""
    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.error(request, '您已登录!')
            return HttpResponseRedirect(reverse('gather.views.index'))
        return func(request, *args, **kwargs)
    return returned_wrapper
