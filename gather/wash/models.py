#!/usr/bin/python
#!-*- coding: UTF-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum

from gather.celery import send_wechat_msg


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
    pid = models.IntegerField('省份')
    name = models.CharField('名称', max_length=255)

    @classmethod
    def get_name(cls, id):
        try:
            return cls.objects.get(pk=id).name
        except:
            return ''

    @classmethod
    def get_id(cls, name):
        try:
            return cls.objects.get(name=name).id
        except:
            return ''

class IndexBanner(models.Model):
    """ 首页轮播图"""
    photo = models.CharField('url', max_length=255)
    index = models.IntegerField('排序')
    is_show = models.BooleanField('是否显示', default=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def get_photo_url(self):
        return "http://7xkqb1.com1.z0.glb.clouddn.com/{}".format(self.photo)


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
    name = models.CharField('姓名', max_length=255)
    phone = models.CharField('电话', max_length=20)
    province = models.CharField('省份', max_length=100)
    city = models.CharField('城市', max_length=100)
    country = models.CharField('镇', max_length=100, null=True)
    street = models.CharField('街道', max_length=255, null=True)
    mark = models.CharField('详细地址', max_length=255, null=True)
    is_default = models.BooleanField('是否是默认地址', default=False)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def detail(self):
        return u"{} {} {} {} {}".format(self.province, self.city, self.country, self.street, self.mark)

    @classmethod
    def has_default(cls, user):
        return cls.objects.filter(user=user, is_default=True).exists()

    @classmethod
    def get_default(cls, user, choose=None):
        try:
            if choose is None:
                return cls.objects.get(user=user, is_default=True)
            else:
                return cls.objects.get(user=user, id=choose)
        except:
            return None

class WashType(models.Model):
    """ 洗刷类型"""
    MEASURE = (
        (1, u'只'),
        (2, u'双'),
        (3, u'件'),
        (4, u'套'),
        (5, u'条')
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
        if self.photo:
            return "http://7xkqb1.com1.z0.glb.clouddn.com/{}".format(self.photo)
        return "/static/img/av1.png"


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
    wash_type = models.IntegerField('优惠对象', choices=WashType.WASH_TYPE, default=7)
    discount_type = models.IntegerField('折扣类型', choices=DISCOUNT_TYPE, default=1)
    is_valid = models.BooleanField('是否有效', default=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def delete(self):
        self.is_valid = False
        self.save()


class Basket(models.Model):
    """ 购物车"""
    sessionid = models.CharField('sessionid', max_length=255, null=True)
    wash_id = models.IntegerField()
    count = models.IntegerField('数量', default=0)
    is_valid = models.BooleanField('是否有效', default=True)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    @classmethod
    def is_sessionid_exist(cls, sessionid):
        return cls.objects.filter(sessionid=sessionid, is_valid=True).exists()

    @classmethod
    def is_wash_exist(cls, sessionid, wash_id):
        return cls.objects.filter(sessionid=sessionid, wash_id=wash_id, is_valid=True).exists()

    @classmethod
    def update(cls, sessionid, wash_id, flag='add'):
        if cls.is_wash_exist(sessionid, wash_id):
            basket = Basket.objects.get(sessionid=sessionid, wash_id=wash_id, is_valid=True)
            if flag == 'add':
                basket.count += 1
            else:
                if basket.count > 0:
                    basket.count -= 1
            basket.save()

    @classmethod
    def get_list(cls, sessionid):
        if cls.is_sessionid_exist(sessionid):
            baskets = cls.objects.filter(sessionid=sessionid, is_valid=True, count__gt=0)
            basket_dict = {}
            for basket in baskets:
                basket_dict[basket.wash_id] = basket.count
            return basket_dict
        else:
            return {}

    @classmethod
    def total(cls, sessionid):
        t = cls.objects.filter(sessionid=sessionid, is_valid=True).aggregate(Sum('count'))['count__sum']
        return t if t is not None else 0

    @classmethod
    def submit(cls, sessionid):
        cls.objects.filter(sessionid=sessionid).update(is_valid=False)


PAY = (
    (0, '微信'),
    (1, '货到付款')
)

STATUS = (
    (0, u'未付款'),
    (1, u'已提交,未处理'),
    (2, u'确认,取货中'),
    (3, u'已取,清洗中'),
    (4, u'清洗完毕, 派送中'),
    (5, u'交易结束'),
    (6, u'交易失败'),
    (7, u'买家取消交易'),
    (8, u'卖家取消交易'),
    (9, u'已过期'),

)


class Order(models.Model):
    """ 订单概览"""
    SERVICE_TIME_CHOICE = (
        (0, '上午'),
        (1, '下午')
    )

    user = models.ForeignKey(WashUserProfile, related_name='orders')
    address = models.ForeignKey(UserAddress, related_name='order_address')
    discount = models.ForeignKey(Discount, related_name='order_discount', null=True)
    mark = models.CharField('备注', max_length=255, null=True)
    money = models.IntegerField('总价', default=0)
    pay_method = models.IntegerField('付款方式', choices=PAY, default=1)
    service_begin = models.DateTimeField('服务开始时间', blank=True, null=True)
    service_end = models.DateTimeField('服务结束时间', blank=True, null=True)
    service_time = models.DateTimeField('要求服务时间', blank=True, null=True)
    am_pm = models.IntegerField('时间段', choices=SERVICE_TIME_CHOICE, default=0)
    pay_date = models.DateTimeField('付款日期', blank=True, null=True)
    status = models.IntegerField('订单状态', choices=STATUS, default=1)
    verify_code = models.IntegerField('订单确认码')

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    @classmethod
    def exists(cls, oid):
        return cls.objects.filter(pk=oid).exists()

    @classmethod
    def status_next(cls, oid, verify_code=None):
        if cls.exists(oid):
            order = Order.objects.get(pk=oid)
            if order.status < 5:
                param = {
                    'status': order.status+1
                }
                user = order.user.user
                if order.status == 1:
                    param['service_begin'] = datetime.datetime.now()
                    send_wechat_msg(user, 'order_get', oid)
                elif order.status == 3:
                    send_wechat_msg(user, 'order_post', oid, {'verify_code': {'value': order.verify_code, 'color': '#173177'}})
                if order.status == 4:
                    if verify_code == order.verify_code:
                        send_wechat_msg(user, 'order_succ', oid)
                        param['service_end'] = datetime.datetime.now()
                    else:
                        return False

                cls.objects.filter(pk=oid).update(**param)
                OrderLog.create(oid, order.status+1)
                return True

    @classmethod
    def status_back(cls, oid):
        if cls.exists(oid):
            order = Order.objects.get(pk=oid)
            if order.status > 1 and order.status < 5:
                cls.objects.filter(pk=oid).update(status=order.status-1)
                OrderLog.create(oid, order.status-1)
                return True
        return False

    @classmethod
    def status_close(cls, oid, is_buyer=True):
        if cls.exists(oid):
            order = cls.objects.get(pk=oid)
            user = order.user.user
            if is_buyer:
                if cls.objects.get(pk=oid).status == 1:
                    OrderLog.create(oid, 7)
                    cls.objects.filter(pk=oid).update(status=7)
                    send_wechat_msg(user, 'order_close', oid)
                    return True
            else:
                cls.objects.filter(pk=oid).update(status=8)
                OrderLog.create(oid, 8)
                send_wechat_msg(user, 'order_close', oid, {'user': {'value': u'卖家', 'color': '#173177'}})
                return True
        return False

class OrderDetail(models.Model):
    """ 订单详情"""
    order = models.ForeignKey(Order, related_name='order_general')
    wash_type_id = models.IntegerField()
    count = models.IntegerField('数量', default=0)
    price = models.IntegerField('购买时价格', default=0)
    name = models.CharField('名称', max_length=50)
    measure = models.IntegerField('单位', choices=WashType.MEASURE, default=1)
    belong = models.IntegerField('所属', choices=WashType.WASH_TYPE, default=1)
    photo = models.CharField('图片', max_length=255)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    def get_photo_url(self):
        if self.photo:
            return "http://7xkqb1.com1.z0.glb.clouddn.com/{}".format(self.photo)
        return "/static/img/av1.png"


class OrderLog(models.Model):
    """订单状态记录"""
    order = models.ForeignKey(Order, related_name='order_log')
    status = models.IntegerField('订单状态', choices=STATUS, default=1)

    created = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField('最后更新时间', auto_now=True)

    @classmethod
    def create(cls, oid, status):
        cls(order_id=oid, status=status).save()

