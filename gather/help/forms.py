#!/usr/bin/python
#!-*- coding: utf-8 -*-

import datetime
import logging

from django import forms

from help.models import Help

class AddHelpForm(forms.ModelForm):
    """ 添加拜托表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(AddHelpForm, self).__init__(*args, **kwargs)
        self._request = request
    class Meta:
        model = Help
        fields = ('title', 'connect_method', 'content', 'latitude', 'longitude', 'remark', 'cancel_time')

    title = forms.CharField(label='标题', max_length=50)
    connect_method = forms.CharField(label='联系方式', max_length=50)
    content = forms.CharField(label='内容', max_length=400, required=False)
    latitude = forms.FloatField(label='维度')
    longitude = forms.FloatField(label='经度')
    remark = forms.CharField(label='备注', max_length=400, required=False)
    cancel_time = forms.DateField(label='失效时间', required=False)

    def clean_title(self):
        title = self.cleaned_data['title']
        if not title:
            raise forms.ValidationError('标题不能为空')
        elif(len(title)>50):
            raise forms.ValidationError('标题最多容纳50个字符')
        return title

    def clean_connect_method(self):
        connect_method = self.cleaned_data['connect_method']
        if not connect_method:
            raise forms.ValidationError('联系方式不能为空')
        elif(len(connect_method)>50):
            raise forms.ValidationError('联系方式最长50个字符')
        return connect_method

    def clean(self):
        print self.errors
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(AddHelpForm, self).save(commit=False)
        m.seeker = self._request.user
        if commit:
            m.save()
        return m
