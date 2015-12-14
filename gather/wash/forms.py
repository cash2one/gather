#!/usr/bin/python
#!-*- coding: utf-8 -*-

import datetime
import logging

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login

from account.models import LoginLog
from wash.models import WashUserProfile, VerifyCode, WashType, Discount, IndexBanner
from wash.models import Company
from wechat.models import WeProfile
from utils import gen_info_msg, gen_photo_name, yuan_to_fen
from qn import Qiniu

LOGIN_LOG = logging.getLogger('login')
INFO_LOG = logging.getLogger('info')


class RegistForm(forms.Form):
    """ 注册登录表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(RegistForm, self).__init__(*args, **kwargs)
        self._request = request

    phone = forms.CharField(label='手机号', max_length=11, widget=forms.TextInput(attrs={'placeholder': '请输入手机号', 'class': 'form-control'}), error_messages={'required': '请输入手机号'})
    code = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=False), error_messages={'required': '请输入验证码'})

    def clean_phone(self):

        phone = self.cleaned_data['phone']
        try:
            int(phone)
            if len(phone) != 11:
                raise ValueError
        except ValueError:
            raise forms.ValidationError('手机号格式错误')

        return self.cleaned_data['phone']

    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            int(code)
            if len(code) != 4:
                raise ValueError
        except ValueError:
            raise forms.ValidationError('验证码格式错误!')

        return self.cleaned_data['code']

    def clean(self):
        if self.errors:
            return
        phone = self.cleaned_data['phone']
        code = self.cleaned_data['code']
        open_id = self._request.POST.get('open_id', '')
        short = self._request.POST.get('short', '')
        if not VerifyCode.code_expire(phone):
            if VerifyCode.code_valid(phone, code):
                if not WashUserProfile.objects.filter(phone=phone).exists():
                    user, created = User.objects.get_or_create(username=phone)
                    user.set_password("111111")
                    user.save()
                    if open_id:
                        WeProfile(user=user, open_id=open_id).save()

                    extra_param = {}
                    if short:
                        if Company.exists(short):
                            company = Company.objects.get(short=short)
                            extra_param["is_company_user"] = True
                            extra_param["company"] = company

                    WashUserProfile(user=user, phone=phone, is_phone_verified=True,
                                    phone_verified_date=datetime.datetime.now(), **extra_param).save()
            else:
                raise forms.ValidationError('验证码输入错误!')
        else:
            raise forms.ValidationError('验证码已过期,请重新获取!')

        return self.cleaned_data

    def login(self):
        phone = self.cleaned_data['phone']
        user = authenticate(remote_user=phone)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self._request, user)


class WashTypeForm(forms.ModelForm):
    """ 洗刷添加表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(WashTypeForm, self).__init__(*args, **kwargs)
        self._request = request

    class Meta:
        model = WashType
        fields = ('name', 'new_price', 'old_price', 'mark', 'measure', 'belong', 'is_for_company')

    name = forms.CharField(label='名称', widget=forms.TextInput(attrs={'placeholder': '请输入名称'}), error_messages={'required': '请输入名称'})
    new_price = forms.CharField(label='现价', widget=forms.TextInput(attrs={'placeholder': '请输入现价'}), error_messages={'required': '请输入名称'})
    old_price = forms.CharField(label='旧价', widget=forms.TextInput(attrs={'placeholder': '请输入旧价'}), error_messages={'required': '请输入名称'})
    mark = forms.CharField(label='备注', initial='')
    measure = forms.ChoiceField(label=u'单位', choices=WashType.MEASURE, widget=forms.RadioSelect())
    belong = forms.ChoiceField(label=u'所属', choices=WashType.WASH_TYPE, widget=forms.RadioSelect())
    is_for_company = forms.IntegerField(label=u'是否公司合作', )

    def clean(self):
        new_price = yuan_to_fen(self.cleaned_data['new_price'])
        old_price = yuan_to_fen(self.cleaned_data['old_price'])
        self.cleaned_data['new_price'] = new_price
        self.cleaned_data['old_price'] = old_price
        return self.cleaned_data

    def save(self, commit=True):
        m = super(WashTypeForm, self).save(commit=False)
        try:
            q = Qiniu()
            local_file = self._request.FILES['photo'].file
            image_name = gen_photo_name() + "." + self._request.FILES['photo']._name.encode('utf-8').split(".")[-1]
            q.upload_stream(image_name, local_file)
        except KeyError:
            image_name = m.photo

        m.photo = image_name
        m.save()


class DiscountForm(forms.ModelForm):
    """ 优惠券添加表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        self._request = request

    class Meta:
        model = Discount
        fields = ('name', 'price', 'begin', 'end', 'wash_type', 'discount_type', 'range_type', 'present_type')

    name = forms.CharField(label='名称', widget=forms.TextInput(attrs={'placeholder': '请输入名称'}), error_messages={'required': '请输入名称'})
    price = forms.CharField(label='优惠规格', widget=forms.TextInput(attrs={'placeholder': '输入优惠价格或者折扣'}), error_messages={'required': '请输入名称'})
    begin = forms.CharField(label='开始时间')
    end = forms.CharField(label='结束时间')
    wash_type = forms.ChoiceField(label=u'优惠对象', choices=WashType.WASH_TYPE, widget=forms.RadioSelect())
    discount_type = forms.ChoiceField(label=u'优惠类型', choices=Discount.DISCOUNT_TYPE, widget=forms.RadioSelect())
    range_type = forms.ChoiceField(label=u'优惠范围', choices=Discount.RANGE_TYPE, widget=forms.RadioSelect())
    present_type = forms.ChoiceField(label=u'赠送范围', choices=Discount.PRESENT_TYPE, widget=forms.RadioSelect())

    def clean(self):
        wash_type = self.cleaned_data['wash_type']
        range_type = self.cleaned_data['range_type']
        wash_id = self._request.POST.get('wash', '0')
        u = self._request.POST.get('update', 'no')
        company_id = self._request.POST.get('company', '0')
        is_for_user = self._request.POST.get('is_for_user', '0')
        company_id = None if company_id == '0' else company_id
        wash_id = None if wash_id == '0' else wash_id
        today = datetime.datetime.now()

        if range_type == u'1':
            # 全部类型 折扣和减钱只能有一个
            if Discount.objects.filter(status=True, range_type=range_type, begin__lte=today,
                                       end__gte=today, company_id=company_id, is_for_user=is_for_user).exists():
                raise forms.ValidationError(u'已存在同类型的有效优惠券或折扣和减钱只能有一个!')
        elif range_type == u'2':
            # 一类 折扣和减钱只能有一个
            if Discount.objects.filter(wash_type=wash_type, status=True, range_type=range_type,
                                       begin__lte=today, end__gte=today,
                                       company_id=company_id, is_for_user=is_for_user).exists():
                raise forms.ValidationError(u'已存在同类型的有效优惠券或折扣和减钱只能有一个!')
        elif range_type == u'3':
            # 某一个产品
            if Discount.objects.filter(wash_type=wash_type, status=True, wash_id=wash_id,
                                       range_type=range_type, begin__lte=today, end__gte=today,
                                       company_id=company_id, is_for_user=is_for_user).exists():
                raise forms.ValidationError(u'已存在同类型的有效优惠券或折扣和减钱只能有一个!')
        return self.cleaned_data

    def save(self, commit=True, force_update=False):
        m = super(DiscountForm, self).save(commit=False)
        company_id = self._request.POST.get('company', '0')
        wash_id = self._request.POST.get('wash', '0')

        if company_id != '0':
            m.company_id = company_id
        if wash_id != '0':
            m.wash_id = wash_id

        is_for_user = self._request.POST.get('is_for_user', '0')
        m.is_for_user = True if is_for_user == '1' else False
        m.save()


class IndexForm(forms.ModelForm):
    """ 轮播图添加表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(IndexForm, self).__init__(*args, **kwargs)
        self._request = request

    class Meta:
        model = IndexBanner
        fields = ('index', 'is_show')

    index = forms.CharField(label='顺序')
    is_show = forms.ChoiceField(label=u'是否显示', choices=((True, u'显示'), (False, u'不显示')), widget=forms.RadioSelect())

    def clean(self):
        return self.cleaned_data

    def save(self, commit=True):
        m = super(IndexForm, self).save(commit=False)
        try:
            q = Qiniu()
            local_file = self._request.FILES['photo'].file
            image_name = gen_photo_name() + "." + self._request.FILES['photo']._name.encode('utf-8').split(".")[-1]
            q.upload_stream(image_name, local_file)
        except KeyError:
            image_name = m.photo

        m.photo = image_name
        m.save()
