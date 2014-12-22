#!/usr/bin/python
#!-*- coding: utf-8 -*-

import datetime
import logging

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login

from account.models import UserProfile, LoginLog

from utils import gen_info_msg

LOGIN_LOG = logging.getLogger('login')
INFO_LOG = logging.getLogger('info')


class LoginForm(forms.Form):
    """ 登录表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self._request = request

    username = forms.CharField(label='用户名', max_length=30, widget=forms.TextInput(attrs={'placeholder': '请输入您的用户名'}), error_messages={'required': '请输入您的用户名'})
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=False), error_messages={'required': '请输入您的密码'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' not in username:
            LoginLog(
                username=username,
                login_ip=self._request.META['REMOTE_ADDR'],
                is_succ=False,
                fail_reason='非邮箱登陆',
            ).save()
            LOGIN_LOG.info(gen_info_msg(self._request, action=u'非邮箱登陆'))
            raise forms.ValidationError('请用邮箱登录')
        elif not User.objects.filter(username=username).exists():
            LoginLog(
                username=username,
                login_ip=self._request.META['REMOTE_ADDR'],
                is_succ=False,
                fail_reason='未注册',
            ).save()
            LOGIN_LOG.info(gen_info_msg(self._request, action=u'未注册'))
            raise forms.ValidationError('您还未注册')
        return self.cleaned_data['username']

    def clean(self):
        if self.errors:
            return
        password = self.cleaned_data['password']
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if not user.check_password(password):
                LoginLog(
                    username=username,
                    login_ip=self._request.META['REMOTE_ADDR'],
                    is_succ=False,
                    fail_reason='密码错误',
                ).save()
                LOGIN_LOG.info(gen_info_msg(self._request, action=u'密码输入错误'))
                raise forms.ValidationError('密码输入错误')
        return self.cleaned_data

    def login(self):
        username = self.cleaned_data['username']
        user = authenticate(username=username, password=self.cleaned_data['password'])
        login(self._request, user)
        LoginLog(
            username=username,
            login_ip=self._request.META['REMOTE_ADDR'],
            is_succ=True,
        ).save()
        LOGIN_LOG.info(gen_info_msg(self._request, action=u'登陆成功'))


class RegistForm(forms.Form):
    """ 注册表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(RegistForm, self).__init__(*args, **kwargs)
        self._request = request

    username = forms.CharField(label='用户名', max_length=30, widget=forms.TextInput(attrs={'placeholder': '请输入您的用户名'}), error_messages={'required': '请输入您的用户名'})
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=False), error_messages={'required': '请输入您的密码'})
    confirm_password = forms.CharField(label='再次输入', widget=forms.PasswordInput(render_value=False), error_messages={'required': '请再次输入密码'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' not in username:
            INFO_LOG.info(gen_info_msg(self._request, action=u'未用邮箱注册'))
            raise forms.ValidationError('请用邮箱注册')
        elif User.objects.filter(username=username).exists():
            INFO_LOG.info(gen_info_msg(self._request, action=u'已注册用户注册'))
            raise forms.ValidationError('您已注册, 请登录')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if ' ' in password or ' ' in confirm_password:
            raise forms.ValidationError('密码中不能包含空格')
        elif len(password) == 0 or len(confirm_password) == 0:
            raise forms.ValidationError('密码中不能为空')
        elif password != confirm_password:
            raise forms.ValidationError('两次密码输入不同')
        return self.cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User(
            username=username,
            email=username,
            is_active=False,
        )
        user.set_password(password)
        user.save()

        profile = UserProfile(
            user=user,
            username=username,
            nickname=username,
            email=username,
            is_mail_verified=False,
        )
        profile.save()

        INFO_LOG.info(gen_info_msg(self._request, action=u'注册成功'))
        return profile










               