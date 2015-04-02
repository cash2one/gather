#!/usr/bin/python
# -*- coding:utf-8 -*-

import base64
import datetime
import logging

from django.conf import settings
from django.contrib import messages
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from functools import wraps

from account.models import ClickLog

from utils import gen_info_msg

ONE_DAY = 24 * 60 * 60

CLICK_LOG = logging.getLogger('click')
INFO_LOG = logging.getLogger('info')


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
            value = base64.b64decode(code)
            signer = TimestampSigner()
            try:
                username = signer.unsign(value, ONE_DAY)
                INFO_LOG.info(gen_info_msg(request, action='链接正常', code_url=request.path, valid=True, username=username))
                return func(request, *args, **kwargs)
            except (SignatureExpired, BadSignature, TypeError), e:
                username = signer.unsign(value)
                if isinstance(e, SignatureExpired):
                    messages.error(request, '链接已失效')
                    INFO_LOG.info(gen_info_msg(request, action=u'链接已失效', code_url=request.path, valid=False, username=username))
                elif isinstance(e, BadSignature):
                    messages.error(request, '链接被篡改')
                    INFO_LOG.info(gen_info_msg(request, action=u'链接被篡改', code_url=request.path, valid=False, username=username))
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            INFO_LOG.info(gen_info_msg(request, action=u'无code信息', code_url=request.path, valid=False, username=username))
            return HttpResponseRedirect(settings.LOGIN_URL)
    return returned_wrapper


def unlogin_required(func):
    """ 不允许登录用户进入"""
    @wraps(func)
    def returned_wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.error(request, '您已登录!')
            INFO_LOG.info(gen_info_msg(request, action=u'已登陆不能进入', url=request.path, username=request.user.username))
            return HttpResponseRedirect(reverse('gather.views.index'))
        return func(request, *args, **kwargs)
    return returned_wrapper
