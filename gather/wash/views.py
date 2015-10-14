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

from wash.models import VerifyCode, WashUserProfile, WashType, IndexBanner
from wash.models import Basket, UserAddress, Address, Order, OrderDetail
from wash.forms import RegistForm
from CCPRestSDK import REST
from utils import gen_verify_code, adjacent_paginator

WASH_URL = settings.WASH_URL


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


def regist(request, form_class=RegistForm, template_name='wash/regist.html'):
    if request.method == "POST":
        form = form_class(request, data=request.POST)
        if form.is_valid():
            form.login()
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
                # 临时
                user = authenticate(remote_user=phone)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return HttpResponse(json.dumps({"result": True, 'msg': 'login'}))
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


def index(request, template_name='wash/index.html'):
    img_list = IndexBanner.objects.filter(is_show=True).order_by("index")
    imgs, page_numbers = adjacent_paginator(img_list, page=request.GET.get('page', 1))
    return render(request, template_name, {
        'imgs': imgs,
        'page_numbers': page_numbers
    })


def show(request, template_name='wash/show.html'):
    wash_arr = get_show_info(request)
    if request.is_ajax():
        return HttpResponse(json.dumps({'status': True, 'result': wash_arr}))

    return render(request, template_name, {
        'wash_arr': wash_arr,
    })


def basket(request, template_name='wash/basket.html'):
    """
    购物车
    :param request:
    :param template_name:
    :return:
    """
    wash_arr = basket_info(request)
    return render(request, template_name, {
        'wash_arr': wash_arr,
    })


@login_required(login_url=WASH_URL)
def order(request, template_name="wash/order.html"):
    """
    下单
    :param request:
    :return:
    """
    profile = request.user.wash_profile
    wash_list = basket_info(request)
    price_sum = reduce(lambda x, y: x+y, [wash['count']*wash['new_price']for wash in wash_list])

    if request.method == "POST":
        address_id = request.POST.get('address_id')
        service_time = request.POST.get('service_time')
        am_pm = request.POST.get('am_pm')
        mark = request.POST.get('mark')

        order = Order(user=profile, address_id=address_id, mark=mark,
                      money=price_sum, service_time=service_time, am_pm=am_pm)
        order.save()
        for wash in wash_list:
            OrderDetail(order=order, wash_type_id=wash['id'],
                        count=wash['count'], price=wash['new_price']).save()
        Basket.submit(request.session.session_key)
        return HttpResponseRedirect(reverse('wash.views.user_order'))
    else:
        choose = request.GET.get('choose', None)
        address = UserAddress.get_default(profile, choose)
    return render(request, template_name, {
        'address': address,
        'profile': profile,
        'wash_list': wash_list,
        'price_sum': price_sum,
        'today': datetime.datetime.now(),
    })


@csrf_exempt
def basket_update(request):
    if request.method == "POST" and request.is_ajax():
        wash_id = request.POST.get('key')
        flag = request.POST.get('flag')
        sessionid = request.session.session_key
        if Basket.is_sessionid_exist(sessionid):
            if Basket.is_wash_exist(sessionid, wash_id):
                Basket.update(sessionid, wash_id, flag)
            else:
                Basket(sessionid=sessionid, wash_id=wash_id, count=1).save()
        else:
            Basket(sessionid=sessionid, wash_id=wash_id, count=1).save()
    return HttpResponse(json.dumps(True))


def get_show_info(request):
    # 洗刷清单页
    belong = request.GET.get('belong', '2')
    wash_list = WashType.objects.filter(belong=belong)
    washes, page_numbers = adjacent_paginator(wash_list, page=request.GET.get('page', 1))
    return basket_info(request, washes)


def basket_info(request, washes=None):
    # 组装预购数据, 同时可用来反馈用户选择了哪些商品
    sessionid = request.session.session_key
    basket_list = Basket.get_list(sessionid)
    if washes is None:
        washes = WashType.objects.filter(id__in=basket_list.keys())

    wash_arr = []
    for wash in washes:
        w = {}
        w['id'] = wash.id
        w['name'] = wash.name
        w['new_price'] = wash.new_price
        w['old_price'] = wash.old_price
        w['measure'] = wash.get_measure_display()
        w['belong'] = wash.get_belong_display()
        w['photo'] = wash.get_photo_url()
        w['count'] = basket_list.get(wash.id, 0)
        wash_arr.append(w)
    return wash_arr


@login_required(login_url=WASH_URL)
def user_address(request, template_name="wash/address.html"):
    addresses = UserAddress.objects.filter(user=request.user.wash_profile)
    return render(request, template_name, {
        'addresses': addresses,
    })


@login_required(login_url=WASH_URL)
def user_address_select(request, template_name="wash/address_select.html"):
    addresses = UserAddress.objects.filter(user=request.user.wash_profile)
    return render(request, template_name, {
        'addresses': addresses,
    })


@login_required(login_url=WASH_URL)
def user_address_add(request, template_name="wash/address_add.html"):
    if request.method == 'POST':
        country_id = request.POST.get('country', '')
        country = Address.get_name(country_id)
        street = request.POST.get('street', '')
        mark = request.POST.get('mark', '')
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')

        if UserAddress.has_default(request.user.wash_profile):
            is_default = False
        else:
            is_default = True
        UserAddress(user=request.user.wash_profile,
                    province=u'北京',
                    city=u'北京',
                    name=name,
                    phone=phone,
                    country=country,
                    street=street,
                    mark=mark,
                    is_default=is_default).save()
        return HttpResponseRedirect(reverse('wash.views.user_address'))
    else:
        countrys = Address.objects.filter(pid=1101)
        streets = Address.objects.filter(pid=110101)
        place = request.GET.get('place')
    return render(request, template_name, {
        'countrys': countrys,
        'streets': streets,
        'place': place,
    })


def address_street(request):
    # ajax获取街道信息
    if request.is_ajax():
        pid = request.GET.get('pid', 0)
        streets = Address.objects.filter(pid=pid)
        street_arr = []
        for street in streets:
            street_arr.append(street.name)
        return HttpResponse(json.dumps({'result': True, 'info': street_arr}))


@login_required(login_url=WASH_URL)
def user_address_update(request, template_name="wash/address_update.html"):
    return render(request, template_name)


#@auto_login
def account(request, template_name='wash/account.html'):
    user = request.user
    if user.is_authenticated():
        profile = WashUserProfile.objects.get(user=user)
    else:
        profile = None
    return render(request, template_name, {
        'profile': profile
    })


@login_required(login_url=WASH_URL)
def user_order(request, template_name="my_order.html"):
    return render(request, template_name)


@login_required(login_url=WASH_URL)
def user_discount(request, template_name="my_order.html"):
    return render(request, template_name)

