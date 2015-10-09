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
from wash.models import IndexBanner
from account.models import LoginLog
from wash.forms import RegistForm, WashTypeForm, DiscountForm, IndexForm
from CCPRestSDK import REST
from utils import gen_verify_code, adjacent_paginator


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
def user_list(request, template_name="wash/manage/user_list.html"):
    user_list = WashUserProfile.objects.all()
    return render(request, template_name, {
        'user_list': user_list,
    })


@login_required(login_url='/wash/manage/')
def wash_img(request, template_name='wash/manage/index_imgs.html'):
    img_list = IndexBanner.objects.all()
    imgs, page_numbers = adjacent_paginator(img_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'imgs': imgs,
        'page_numbers': page_numbers
    })


@login_required(login_url='/wash/manage/')
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


@login_required(login_url='/wash/manage/')
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



@login_required(login_url='/wash/manage/')
def wash_type(request, template_name="wash/manage/wash_type.html"):
    """
    洗刷类型清单
    :param request:
    :param template_name:
    :return:
    """
    wash_list = WashType.objects.all()
    wash_types, page_numbers = adjacent_paginator(wash_list, page=request.GET.get('page', 1))
    return render(request, template_name, {
        'wash_types': wash_types,
        'page_numbers': page_numbers

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
            return HttpResponseRedirect(reverse("wash.mviews.wash_type"))
    form = form_class()
    return render(request, template_name, {
        'measures': WashType.MEASURE,
        'belongs': WashType.WASH_TYPE,
        'form': form,
    })


@login_required(login_url='/wash/manage/')
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


@login_required(login_url='/wash/manage/')
def model_del(request, model_type, type_id):
    """
    类型删除
    :param request:
    :return:
    """
    try:

        if model_type == 'wash_type':
            model = WashType
        m = model.objects.get(id=type_id)
        m.delete()
        return HttpResponseRedirect(reverse("wash.mviews.wash_type"))
    except model.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse("wash.mviews.wash_type"))


@login_required(login_url='/wash/manage/')
def discount(request, template_name="wash/manage/discount.html"):
    """
    优惠券列表
    :param request:
    :param template_name:
    :return:
    """
    discounts_list = Discount.objects.all()
    discounts, page_numbers = adjacent_paginator(discounts_list, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'discounts': discounts,
        'page_numbers': page_numbers
    })


@login_required(login_url='/wash/manage/')
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
    form = form_class()
    return render(request, template_name, {
        'form': form,
    })


@login_required(login_url='/wash/manage/')
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
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("wash.mviews.discount"))
        form = form_class(instance=discount)
        messages.info(request, u"修改成功")
        return render(request, template_name, {
            'form': form,
            'discount': discount,
        })
    except WashType.DoesNotExist:
        messages.error(request, u"类型不存在")
    return HttpResponseRedirect(reverse("wash.mviews.discount"))


@login_required(login_url='/wash/manage/')
def order(request, template_name="wash/manage/order.html"):
    """
    订单概览列表
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        pass
    orders = Order.objects.all()
    order_list, page_numbers = adjacent_paginator(orders, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'order_list': order_detail,
        'page_number': page_numbers,
    })


@login_required(login_url='/wash/manage/')
def order_detail(request, order_id='0', template_name="wash/manage/order.html"):
    """
    订单概览列表
    :param request:
    :param template_name:
    :return:
    """
    if request.method == "POST":
        pass
    if order_id == '0':
        details = OrderDetail.objects.all()
    else:
        details = OrderDetail.objects.filter(order_id=order_id)

    detail_list, page_numbers = adjacent_paginator(details, page=request.GET.get('page', 1))

    return render(request, template_name, {
        'detail_list': detail_list,
    })
