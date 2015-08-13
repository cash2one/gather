#!/usr/bin/python
#!-*- coding: utf-8 -*-

from django import forms

from share.models import Share

from utils import gen_photo_name, get_image_x_y
from qn import Qiniu


class ShareForm(forms.ModelForm):
    """ 提交分享表单"""
    def __init__(self, request=None, *args, **kwargs):
        super(ShareForm, self).__init__(*args, **kwargs)
        self._request = request

    class Meta:
        model = Share
        fields = ('title', 'photo', 'content')

    def clean_title(self):
        if len(self.cleaned_data['title']) < 1:
            raise forms.ValidationError('标题过短')
        elif len(self.cleaned_data['title']) > 250:
            raise forms.ValidationError('标题过长')
        return self.cleaned_data['title']

    def clean_photo(self):
        try:
            q = Qiniu()
            local_file = self._request.FILES['photo'].file
            image_name = gen_photo_name() + "." + self._request.FILES['photo']._name.encode('utf-8').split(".")[-1]
            q.upload_stream(image_name, local_file)
            """
            photo = self.cleaned_data['photo']
            photo_name = photo.name[:photo.name.rfind('.')]
            ext = photo.name[photo.name.rfind('.') + 1:]
            photo.name = gen_photo_name() + "." + ext
            if not photo_name:
                raise forms.ValidationError('必须上传一个图片。')
            if ext.lower() not in ['jpg', 'png', 'jpeg', 'bmp']:
                raise forms.ValidationError('只允许上传图片格式，不支持gif格式')
            if len(photo) / (1024 * 1024) > 5:
                raise forms.ValidationError('请上传5M以下大小的图片')
            """
        except KeyError:
            image_name = ''
        return image_name

    def clean(self):
        return self.cleaned_data

    def save(self, commit=True):
        m = super(ShareForm, self).save(commit=False)
        m.user = self._request.user
        m.save()
        if m.photo:
            q = Qiniu()
            xsize, ysize = q.get_image_info(m.photo)
            m.xsize = xsize
            m.ysize = ysize
            m.save()
        return m

