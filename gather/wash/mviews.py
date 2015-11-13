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

from wash.models import WashType, WashUserProfile, Discount, Order, OrderDetail
from wash.models import IndexBanner, Company
from account.models import LoginLog
from wash.forms import WashTypeForm, DiscountForm, IndexForm
from utils import adjacent_paginator

WASH_MURL = settings.WASH_MURL

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


@login_required(login_url=WASH_MURL)
def manage_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, u'已成功退出')
    return HttpResponseRedirect(reverse("wash.mviews.manage_login"))


@login_required(login_url=WASH_MURL)
def manage_index(request, template_name="wash/manage/base.html"):
    return render(request, template_name)


@login_required(login_url=WASH_MURL)
def user_list(request, template_name="wash/manage/user_list.html"):
    user_list = WashUserProfile.objects.all().order_by("-updated")
    return render(request, template_name, {
        'user_list': user_list,
    })


@login_required(login_url=WASH_MURL)
def model_del(request, model_type, type_id):
    """
    类型删除
    :param request:
    :return:
    """
    try:

        if model_type == 'wash_type':
            model = WashType
            url = "wash.mviews.wash_type"
        elif model_type == 'img':
            model = IndexBanner
            url = "wash.mviews.wash_img"
        elif model_type == 'discount':
            model = Discount
            url = "wash.mviews.discount"
        m = model.objects.get(id=type_id)
        m.delete()
        return HttpResponseRedirect(reverse(url))
    except model.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse(url))


@login_required(login_url=WASH_MURL)
def wash_img(request, template_name='wash/manage/index_imgs.html'):
    img_list = IndexBanner.objects.all().order_by("-updated")
    imgs, page_numbers = adjacent_paginator(img_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'imgs': imgs,
        'page_numbers': page_numbers
    })


@login_required(login_url=WASH_MURL)
def wash_img_add(request, form_class=IndexForm, template_name="wash/manage/index_img_add.html"):
    """
    轮播图添加
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        form = form_class(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("wash.mviews.wash_img"))
    form = form_class()
    return render(request, template_name, {
        'form': form,
    })


@login_required(login_url=WASH_MURL)
def wash_img_update(request, img_id=0, form_class=IndexForm, template_name="wash/manage/index_img_update.html"):
    """
    轮播图修改
    :param request:
    :param template_name:
    :return:
    """
    try:
        img = IndexBanner.objects.get(id=img_id)
        if request.method == "POST":
            form = form_class(request, instance=img, data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("wash.mviews.wash_img"))
        form = form_class(instance=img)

        return render(request, template_name, {
            'form': form,
            'img': img,
        })
    except IndexBanner.DoesNotExist:
        return HttpResponseRedirect(reverse("wash.mviews.wash_img"))



@login_required(login_url=WASH_MURL)
def wash_type(request, template_name="wash/manage/wash_type.html"):
    """
    洗刷类型清单
    :param request:
    :param template_name:
    :return:
    """
    wash_list = WashType.objects.all().order_by("-updated")
    wash_types, page_numbers = adjacent_paginator(wash_list, page=request.GET.get('page', 1))
    return render(request, template_name, {
        'wash_types': wash_types,
        'page_numbers': page_numbers

    })


@login_required(login_url=WASH_MURL)
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
            return HttpResponseRedirect(reverse("wash.mviews.wash_type"))
    form = form_class()
    return render(request, template_name, {
        'measures': WashType.MEASURE,
        'belongs': WashType.WASH_TYPE,
        'form': form,
    })


@login_required(login_url=WASH_MURL)
def wash_type_update(request, type_id, form_class=WashTypeForm, template_name="wash/manage/wash_type_update.html"):
    """
    洗刷类型修改
    :param request:
    :param template_name:
    :return:
    """
    try:
        wash_type = WashType.objects.get(id=type_id)

        if request.method == "POST":
            form = form_class(request, instance=wash_type, data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("wash.mviews.wash_type"))
        form = form_class(instance=wash_type)
        #messages.info(request, u"修改成功")
        return render(request, template_name, {
            'form': form,
            'type': wash_type,
        })
    except WashType.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse("wash.mviews.wash_type"))


@login_required(login_url=WASH_MURL)
def discount(request, template_name="wash/manage/discount.html"):
    """
    优惠券列表
    :param request:
    :param template_name:
    :return:
    """
    discounts_list = Discount.objects.all().order_by("-updated")
    discounts, page_numbers = adjacent_paginator(discounts_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'discounts': discounts,
        'page_numbers': page_numbers
    })


@login_required(login_url=WASH_MURL)
def discount_add(request, form_class=DiscountForm, template_name="wash/manage/discount_add.html"):
    """
    优惠券添加
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        form = form_class(request, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("wash.mviews.discount"))
    else:
        form = form_class()
    companys = Company.objects.all()
    washes = WashType.objects.all()
    today = datetime.datetime.now()
    next = today + datetime.timedelta(days=30)
    return render(request, template_name, {
        'form': form,
        'companys': companys,
        'washes': washes,
        'today': today,
        'next': next
    })


@login_required(login_url=WASH_MURL)
def discount_update(request, discount_id, form_class=DiscountForm, template_name="wash/manage/discount_update.html"):
    """
    优惠券修改
    :param request:
    :param template_name:
    :return:
    """
    try:
        discount = Discount.objects.get(id=discount_id)

        if request.method == "POST":
            form = form_class(request, instance=discount, data=request.POST)
            discount.name = request.POST.get('name')
            discount.discount_type = request.POST.get('discount_type')
            discount.price = request.POST.get('price')
            discount.begin = request.POST.get('begin')
            discount.end = request.POST.get('end')
            discount.save()
            return HttpResponseRedirect(reverse("wash.mviews.discount"))
        else:
            form = form_class(request, instance=discount)
        companys = Company.objects.all()
        washes = WashType.objects.all()
        return render(request, template_name, {
            'form': form,
            'discount': discount,
            'companys': companys,
            'washes': washes,
        })
    except WashType.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse("wash.mviews.discount"))


@login_required(login_url=WASH_MURL)
def order(request, template_name="wash/manage/order.html"):
    """
    订单概览列表
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        next = request.POST.get('next', None)
        oid = request.POST.get('oid', None)
        cancel = request.POST.get('cancel', None)
        close = request.POST.get('close', None)
        verify_code = request.POST.get('verify_code', None)
        hour = request.POST.get('hour', None)
        if next:
            status = Order.status_next(oid, verify_code=verify_code, hour=hour)
            if not status:
                messages.error(request, u'验证码错误')
        if cancel:
            Order.status_back(oid)
        if close:
            Order.status_close(oid, is_buyer=False)

    order_list = Order.objects.all().order_by("-updated")
    orders, page_numbers = adjacent_paginator(order_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'orders': orders,
        'page_number': page_numbers,
    })


@login_required(login_url=WASH_MURL)
def order_detail(request, order_id='0', template_name="wash/manage/order_detail.html"):
    """
    订单概览列表
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        pass
    if order_id == '0':
        detail_list = OrderDetail.objects.all().order_by('-created')
    else:
        detail_list = OrderDetail.objects.filter(order_id=order_id)

    details, page_numbers = adjacent_paginator(detail_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'details': details,
    })


@login_required(login_url=WASH_MURL)
def company(request, template_name="wash/manage/company_list.html"):
    if request.method == "POST":
        name = request.POST.get('name', '')
        short = request.POST.get('short', '')
        if name and short:
            result = Company.create(name, short)
            if result:
                messages.info(request, u'添加成功')
            else:
                messages.error(request, u'名称或验证码重复')

    companys = Company.objects.all()
    return render(request, template_name, {
        'companys': companys
    })


@login_required(login_url=WASH_MURL)
def company_discount(request, template_name="wash/manage/company_discount.html"):
    company_id = request.GET.get('company_id', '')
    if company_id:
        param = {
            'company_id': company_id
        }
    else:
        param = {}
    discounts = Discount.objects.filter(status=True, **param).order_by('company')
    return render(request, template_name, {
        'discounts': discounts
    })

