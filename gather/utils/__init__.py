#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import traceback
import base64
import os
import hashlib
import string
import time
import random

from decimal import Decimal
from PIL import Image
from datetime import datetime
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib import messages


from random import choice

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings


ERROR_LOG = logging.getLogger('err')
INFO_LOG = logging.getLogger('info')
ONE_DAY = 24 * 60 * 60


def financial_round(amount):
    """ 金额四舍五入"""
    return int(round(amount))


def yuan_to_fen(amount):
    """ 元转化为分"""
    try:
        return int(str(float(amount) * 100).split('.')[0])
    except ValueError:
        return amount


def fen_to_yuan(amount):
    """ 分转化为元"""
    try:
        return int(amount) / 100.00
    except ValueError:
        return amount


def money_format(value):
    """ 分转换为元"""
    try:
        value = str(int(value) / 100.00)
        return '{0:,}'.format(Decimal(value.rstrip('0').rstrip('.')))
    except (ValueError, TypeError):
        return value



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


def gen_verify_code(length=4):
    """ 生成一个随机验证码"""
    password = []
    while len(password) < length:
        password.append(choice(getattr(string, choice(['digits']))))
    return ''.join(password)


def gen_username(length=6):
    """ 生成一个随机英文名"""
    password = []
    while len(password) < length:
        password.append(choice(getattr(string, choice(['lowercase']))))
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


def resize_avatar(request, profile):
    """ 缩小上传图片大小"""
    path = os.path.join(settings.MEDIA_ROOT, str(profile.big_photo))
    f = Image.open(path)
    xsize, ysize = f.size
    if xsize > ysize:
        if xsize > 600:
            f.resize((600, 600 * ysize / xsize), Image.ANTIALIAS).save(path)
    else:
        if ysize > 400:
            f.resize((xsize * 400 / ysize, 400), Image.ANTIALIAS).save(path)


def crop_avatar(request, profile):
    """ 裁剪上传头像"""
    path = os.path.join(settings.MEDIA_ROOT, str(profile.big_photo))
    f = Image.open(path)
    xsize, ysize = f.size
    size = request.POST.get('crop')
    size_arr = size.split(':')
    if size_arr:
        top = int(size_arr[0][:-2])
        left = int(size_arr[1][:-2])
        width = int(size_arr[3][:-2])
        # 未截取图框直接上传
        if top == 0 and left == 0 and width == 0:
            top = 0
            left = 0
            width = ysize/2
    # box变量是一个四元组(左，上，右，下)。
    box = (left, top, width+left, width+top)
    f.crop(box).save(path)


def get_image_x_y(photo):
    """ 获取图片的长宽"""
    path = os.path.join(settings.MEDIA_ROOT, str(photo))
    f = Image.open(path)
    xsize, ysize = f.size
    return xsize, ysize


def get_encrypt_code(username):
    """ 对用户名加密"""
    signer = TimestampSigner()
    code = base64.b64encode(signer.sign(username))
    return code


def get_encrypt_cash(profile):
    key_value = "phone={}&created={}&cash={}".format(profile.phone, profile.created, profile.cash)
    INFO_LOG.info("cash {}".format(profile.cash))
    ency_s = hashlib.md5(key_value).hexdigest()
    return ency_s


def main():
    print get_withdraw_max(2001 * 100)
    # print gen_password(12)
    # print type(yuan_to_fen(Decimal('100.22333'))), yuan_to_fen('100.22533')

if __name__ == '__main__':
    main()
