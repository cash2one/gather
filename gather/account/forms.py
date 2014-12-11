#!/usr/bin/python
#!-*- coding: utf-8 -*-

import datetime

from django import forms
from django.contrib.auth.models import User

from account.models import UserProfile


class LoginForm(forms.Form):
    """ 登录表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self._request = request

    username = forms.CharField(label='用户名', max_length=30, widget=forms.TextInput(attrs={'placeholder': '请输入您的用户名'}), error_messages={'required': '请输入您的用户名'})
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=False), error_messages={'required': '请输入您的密码'})

    def clearn_username(self):
        username = self.cleaned_data['username']
        if '@' not in username:
            raise forms.ValidationError('请用邮箱登录')
        elif not User.objects.filter(username=username).exists():
            raise forms.ValidationError('您还未注册')

        return username

 
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
            raise forms.ValidationError('请用邮箱注册')
        elif User.objects.filter(username=username).exists():
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
        return profile










               