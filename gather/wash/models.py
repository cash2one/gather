#!/usr/bin/python
#!-*- coding: UTF-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class WashUserProfile(models.Model):
    """ 用户注册信息"""
    user = models.OneToOneField(User, related_name='wash_profile')
    phone = models.CharField('电话', max_length=11, unique=True)
    is_phone_verified = models.BooleanField('是否已经通过验证', default=False)
    phone_verified_date = models.DateTimeField('电话通过验证时间', blank=True, null=True)

    avator = models.CharField('头像', max_length=255, blank=True, null=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def get_mask_username(self):
        # 用户名保密
        return self.phone[:3] + "******"

    @classmethod
    def user_valid(cls, user):
        return cls.objects.filter(user=user, is_phone_verified=True).exists()


class Address(models.Model):
    """ 省市县"""
    province = models.CharField('省份', max_length=20)
    city = models.CharField('城市', max_length=20)
    country = models.CharField('镇', max_length=20, null=True)
    street = models.CharField('街道', max_length=50, null=True)


class WeToken(models.Model):
    """ 微信Token"""
    token = models.CharField('ServerToken', max_length=1024, null=True, blank=True)
    expire_time = models.IntegerField('Expire_time', max_length=1024, null=True, blank=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)


class VerifyCode(models.Model):
    """ 验证码"""
    phone = models.CharField('手机号', max_length=11)
    code = models.CharField('验证码', max_length=4)
    is_expire = models.BooleanField('是否过期', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    @classmethod
    def code_expire(cls, phone):
        verify = VerifyCode.objects.get(phone=phone, is_expire=False)
        if (datetime.datetime.today() - verify.created).seconds > settings.VERIFY_CODE_EXPIRE:
            return True
        else:
            return False

    @classmethod
    def code_valid(cls, phone, code):
        if VerifyCode.objects.filter(phone=phone, code=code, is_expire=False).exists():
            return True
        else:
            return False


class UserAddress(models.Model):
    """ 用户地址"""
    user = models.ForeignKey(WashUserProfile, related_name='addresses')
    province = models.CharField('省份', max_length=20)
    city = models.CharField('城市', max_length=20)
    country = models.CharField('镇', max_length=20, null=True)
    street = models.CharField('街道', max_length=50, null=True)
    mark = models.CharField('备注', max_length=100, null=True)
    is_default = models.BooleanField('是否是默认地址', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)


class WashType(models.Model):
    """ 洗刷类型"""
    MEASURE = (
        (1, u'只'),
        (2, u'双'),
        (3, u'件'),
        (4, u'套'),
    )

    WASH_TYPE = (
        (1, u'鞋'),
        (2, u'上衣'),
        (3, u'裤子'),
        (4, u'帽子'),
        (5, u'床上用品'),
        (6, u'其他'),
        (7, u'全部')
    )
    name = models.CharField('名称', max_length=50)
    new_price = models.IntegerField('现价')
    old_price = models.IntegerField('原价')
    measure = models.IntegerField('单位', choices=MEASURE, default=1)
    belong = models.IntegerField('所属', choices=WASH_TYPE, default=1)
    photo = models.CharField('图片', max_length=255)
    mark = models.CharField('备注', max_length=255, blank=True, null=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def get_photo_url(self):
        return "http://7xkqb1.com1.z0.glb.clouddn.com/{}".format(self.photo)


class Discount(models.Model):
    """ 优惠券"""
    DISCOUNT_TYPE = (
        (1, u'金钱'),
        (2, u'折扣')
    )
    name = models.CharField('优惠券名称', max_length=50)
    price = models.CharField('折扣值', max_length=50)
    begin = models.DateTimeField('开始时间')
    end = models.DateTimeField('结束时间')
    wash_type = models.ForeignKey(WashType, related_name='discount_wash_type')
    discount_type = models.IntegerField('折扣类型', choices=DISCOUNT_TYPE, default=1)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)


STATUS = (
    (0, u'未处理'),
    (1, u'已处理, 取货中'),
    (2, u'清洗中'),
    (3, u'清洗完毕, 派送中'),
    (4, u'交易结束'),
    (5, u'交易失败'),
)

class Order(models.Model):
    """ 订单概览"""
    user = models.ForeignKey(WashUserProfile, related_name='orders')
    address = models.ForeignKey(UserAddress, related_name='order_address')
    discount = models.ForeignKey(Discount, related_name='order_discount', null=True)
    mark = models.CharField('备注', max_length=255, null=True)
    money = models.IntegerField('总价', default=0)
    pay_method = models.IntegerField('付款方式', choices=STATUS, default=1)
    service_begin = models.DateTimeField('服务开始时间', blank=True, null=True)
    service_end = models.DateTimeField('服务结束时间', blank=True, null=True)
    status = models.IntegerField('订单状态', choices=STATUS, default=1)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)


class OrderDetail(models.Model):
    """ 订单详情"""
    order = models.ForeignKey(Order, related_name='order_general')
    wash_type = models.ForeignKey(WashType, related_name='order_wash_type')
    count = models.IntegerField('数量', default=0)
    price = models.IntegerField('购买时价格', default=0)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)
