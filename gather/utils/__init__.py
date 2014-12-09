#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import traceback
import base64


import string
import time
import random

from datetime import datetime
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib import messages


from random import choice

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings


ERROR_LOG = logging.getLogger('err')
ONE_DAY = 24 * 60 * 60


def financial_round(amount):
    """ 金额四舍五入"""
    return int(round(amount))


def gen_info_msg(request, action, **kwargs):
    try:
        data = ''
        for key in request.POST.keys():
            if key not in ['password', 'password1', 'csrfmiddlewaretoken']:
                data += '%s=%s ' % (key, request.POST[key])

        for key in kwargs.keys():
            data += '%s=%s ' % (key, kwargs[key])

        user_id = request.user.id if request.user.id else 0
        return 'userid=%d action=%s %s' % (user_id, action, data)
    except Exception:
        ERROR_LOG.error(traceback.format_exc())
        return 'gen_info_msg error'


def gen_password(length=8):
    """ 生成一个随机密码"""
    password = []
    while len(password) < length:
        password.append(choice(getattr(string, choice(['lowercase', 'uppercase', 'digits', 'punctuation']))))
    return ''.join(password)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def adjacent_paginator(queryset, page, page_num=20, adjacent_pages=2):
    """ 分页"""
    paginator = Paginator(queryset, page_num)
    try:
        paged_queryset = paginator.page(page)
    except PageNotAnInteger:
        paged_queryset = paginator.page(1)
    except EmptyPage:
        paged_queryset = paginator.page(paginator.num_pages)

    start_page = max(paged_queryset.number - adjacent_pages, 1)
    end_page = min(paged_queryset.number + adjacent_pages, paginator.num_pages)

    page_numbers = range(start_page, end_page + 1)
    return paged_queryset, page_numbers


def gen_sn():
    """ 生成序列号"""
    return datetime.now().strftime('%Y%m%d%H%M%S%f')


def gen_photo_name():
    """ 生成图片名称"""
    salt = str(random.randint(10000, 90000))
    photo_name = str(int(time.time()*10000)) + salt
    return photo_name


def get_decipher_username(request):
    """ 获取解密过的username"""
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
            username = signer.unsign(value, ONE_DAY)
            return username
        except (SignatureExpired, BadSignature, TypeError), e:
            if isinstance(e, SignatureExpired):
                messages.error(request, '链接已失效')
            elif isinstance(e, BadSignature):
                messages.error(request, '链接被篡改')
            return None
    else:
        return None


def main():
    print get_withdraw_max(2001 * 100)
    # print gen_password(12)
    # print type(yuan_to_fen(Decimal('100.22333'))), yuan_to_fen('100.22533')

if __name__ == '__main__':
    main()
