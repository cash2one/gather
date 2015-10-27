#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import hashlib
import socket
import urllib
import base64
import time
import random
import requests
import traceback
import simplejson as json
import datetime
import xml.etree.ElementTree as ET

from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner, SignatureExpired

from wechat.models import WeToken, WeProfile, WeLoginQR

from utils import gen_password

WASH_URL_EXPIRE = 5 * 60
WASH_USER_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=wash&openid=%s&lang=zh_CN'
WASH_GET_ACCESS_TOKEN = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
WASH_WEB_GRANT = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={app_id}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state=123#wechat_redirect"
WASH_LOGIN_ID = '777'

ERROR_LOG = logging.getLogger('err')

def get_server_access_token():
    """ 获取微信access_token"""
    we_token = WeToken.objects.all()
    if not we_token.exists() or we_token.get(id=1).expire_time < time.time():
        params = {
            'grant_type': 'client_credential',
            'appid': settings.APP_ID,
            'secret': settings.APP_SECRET,
        }
        r = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=params)
        try:
            result = r.json()['access_token']
            expire_time = r.json()['expires_in'] + time.time() - 1200
            instance = WeToken(id=1, token=result, expire_time=expire_time)
            if not we_token.exists():
                instance.save()
            else:
                instance.save(force_update=True)
        except:
            result = None
    else:
        result = we_token.get(pk=1).token
    return result


def get_userinfo_server_token(openid):
    """ 获取关注者的用户信息"""
    token = get_server_access_token()
    if not token:
        return token
    params = {
        'access_token': token,
        'openid': openid,
        'lang': 'zh_CN',
    }
    r = requests.get('https://api.weixin.qq.com/cgi-bin/user/info', params=params)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        return None

MENU_ACCOUNTS_REGISTER = 1
MENU_ACCOUNTS_BALANCE = 2
MENU_ACCOUNTS_TRADELOG = 3
MENU_ACCOUNTS_RECHARGE = 4
MENU_ACCOUNTS_WITHDRAWAL = 5


def create_menu():
    """ 创建微信菜单"""
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % get_server_access_token()
    params = {
       "button": [
            {
               "type": "view",
               "name": "下单",
               "url": "http://www.jacsice.cn/wash/show/"
            },
            {
               "name": "会员中心",
               "sub_button": [
                   {
                       "type": "view",
                       "name": "订单查询",
                       "url": "http://www.jacsice.cn/wash/user/order/"
                    },
                    {
                       "type": "view",
                       "name": "个人中心",
                       "url": "http://www.jacsice.cn/wash/account/"
                    }
               ],
            },
           {
               "name": "服务中心",
               "sub_button": [
                   {
                       "type": "view",
                       "name": "常见问题",
                       "url": "http://www.jacsice.cn/wash/"
                   },
                   {
                       "type": "view",
                       "name": "联系客服",
                       "url": "http://www.jacsice.cn/wash/"
                   },
                   {
                       "type": "view",
                       "name": "意见建议",
                       "url": "http://www.jacsice.cn/wash/"
                   },
                   {
                       "type": "view",
                       "name": "关于我们",
                       "url": "http://www.jacsice.cn/wash/"
                   }
               ],
            },
       ]
    }
    return requests.post(url, data=json.dumps(params, ensure_ascii=False).encode('utf-8'))


def verification(request):
    """ 微信验证"""
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')

    sortlist = [settings.SERVER_TOKEN, timestamp, nonce]
    sortlist.sort()
    sha = hashlib.sha1()
    sha.update("".join(sortlist))
    s = sha.hexdigest()

    if s == signature:
        return True
    return False


def parse_msg(rawmsgstr):
    """ 将消息解析为dict"""
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

TEXT_MSG_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""


def response_text_msg(msg, content):
    s = TEXT_MSG_TPL % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), content)
    return HttpResponse(s)

HELP_INFO = u""" 这是kker的测试内容^_^,在关注时会发给你 """


def help_info(msg):
    return response_text_msg(msg, HELP_INFO)


def is_text_msg(msg):
    return msg['MsgType'] == 'text'


def user_subscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'subscribe'


def user_unsubscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'unsubscribe'


def is_click_msg(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'CLICK'


def is_view_msg(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'VIEW'


def refresh_weprofile(user):
    """ 同步微信帐号信息"""
    try:
        we_profile = user.we_profile
    except WeProfile.DoesNotExist:
        return False
    user_info = get_userinfo_server_token(we_profile.open_id)
    if not user_info:
        we_profile.nick_name = user_info['nickname']
        we_profile.sex = user_info['sex']
        we_profile.language = user_info['language']
        we_profile.city = user_info['city']
        we_profile.province = user_info['province']
        we_profile.headimgurl = user_info['headimgurl']
        we_profile.save(force_insert=True)
        return True
    return False


@transaction.atomic
def handle_subscribe_msg(msg):
    """ 处理用户关注时的事件"""
    open_id = msg['FromUserName']
    is_exists = WeProfile.objects.filter(open_id=open_id).exists()

    if not is_exists:
        user_info = get_userinfo_server_token(open_id)
        WeProfile(
            open_id=user_info['openid'],
            nick_name=user_info['nickname'],
            sex=user_info['sex'],
            language=user_info['language'],
            city=user_info['city'],
            province=user_info['province'],
            country=user_info['country'],
            headimgurl=user_info['headimgurl'],
            subscribe_time=datetime.datetime.fromtimestamp(int(user_info['subscribe_time'])),
            is_subscribed=True,
            is_binded=False,
        ).save()
        return response_text_msg(msg, u'欢迎关注我要洗鞋微信平台;本公司承接团体单位,会所,服装干洗免费取送,职业装定做,工服订做 电话:010-89550098 135-8182-6688')

    else:
        profile = WeProfile.objects.get(open_id=open_id)
        if profile.is_binded:
            return response_text_msg(msg, u'欢迎关注我要洗鞋微信平台;本公司承接团体单位,会所,服装干洗免费取送,职业装定做,工服订做 电话:010-89550098 135-8182-6688')




def wechat_msg(request):
    """ 微信的消息推送"""
    if verification(request):
        data = request.body
        msg = parse_msg(data)
        if user_subscribe_event(msg):
            return handle_subscribe_msg(msg)
        elif msg['EventKey'] == 'ACCOUNT':  # 点击我的账户 click事件
            return account_click(msg)
        elif is_text_msg(msg):
            content = msg['Content']
            return response_text_msg(msg, content)
        elif is_click_msg(msg):
            return handle_click(msg)
        elif is_view_msg(msg):
            return handle_view(msg)
        
    return HttpResponse('message proccessing fail')

SEND_MSG_TPL = {
    "touser": None,
    "msgtype": "text",
    "text": {
        "content": None,
    }
}


def send_msg(id, content):
    """ 服务器发送微信消息"""
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' % get_server_access_token()
    SEND_MSG_TPL['touser'] = id
    SEND_MSG_TPL['text']['content'] = content
    r = requests.post(url, data=json.dumps(SEND_MSG_TPL, ensure_ascii=False).encode('utf-8'))
    return r


def handle_accounts_reigster(msg):
    """ 处理用户点击注册/绑定的事件"""
    open_id = msg['FromUserName']
    we_user = WeProfile.objects.get(open_id=open_id)
    signer = TimestampSigner()
    encrypt_id = base64.b64encode(signer.sign(open_id))

    return response_text_msg(msg, u'欢迎光临')


def handle_click(msg):
    """ 处理用户点击微信菜单事件"""
    key = int(msg['EventKey'])
    if key == MENU_ACCOUNTS_REGISTER:
        return handle_accounts_reigster(msg)
    else:
        return response_text_msg(msg, u'这个功能还在开发中')


def handle_view(msg):
    """ 处理用户点击微信菜单的view事件"""
    return response_text_msg(msg, u'你点击菜单')


def account_click(msg):
    """ 处理用户点击我的账户时间"""
    open_id = msg['FromUserName']
    from_user = msg['ToUserName']
    msg_xml = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>12345678</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>3</ArticleCount>
    <Articles>
    <item>
    <Title><![CDATA[我的账户]]></Title> 
    <Description><![CDATA[我的账户]]></Description>
    <PicUrl><![CDATA[%s/static/styles/img/zc_cash_img.jpg]]></PicUrl>
    <Url><![CDATA[%s/accounts/m/account/?open_id=%s]]></Url>
    </item>
    <item>
    <Title><![CDATA[没有账号？去注册]]></Title> 
    <Description><![CDATA[没有账号？去注册]]></Description>
    <PicUrl><![CDATA[%s/static/styles/img/zc_cash_img.jpg]]></PicUrl>
    <Url><![CDATA[%s/accounts/m/register/?open_id=%s]]></Url>
    </item>
    <item>
    <Title><![CDATA[已有账号？去绑定]]></Title>
    <Description><![CDATA[已有账号？去绑定]]></Description>
    <PicUrl><![CDATA[%s/static/styles/img/safety_01.jpg]]></PicUrl>
    <Url><![CDATA[%s/accounts/m/bind_already_user/?open_id=%s]]></Url>
    </item>
    </Articles>
    </xml> 
    """ % (open_id, from_user, settings.SERVER_URL, settings.SERVER_URL, open_id, settings.SERVER_URL, settings.SERVER_URL, open_id, settings.SERVER_URL, settings.SERVER_URL, open_id)
    return HttpResponse(msg_xml)


@csrf_exempt
def index(request):
    """ 微信消息处理"""
    # hack_fileobject_close()
    if request.method == 'POST':
        return wechat_msg(request)
    else:
        # 微信公共号绑定时需要
        if verification(request):
            return HttpResponse(request.GET.get('echostr', ''))
    create_menu()
    return HttpResponse('For Test WeChat')

WE_GET_CODE = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=123#wechat_redirect'
WE_CODE_TO_ACCESS_TOKEN = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'


def code_get_openid(request):
    """ 通过auth的code获取open_id"""
    code = request.GET.get('code', '')
    open_id = None
    if code:
        params = {
            'appid': settings.APP_ID,
            'secret': settings.APP_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
        }
        r = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token', params=params)
        try:
            r = r.json()
            open_id = r['openid']
            return True, open_id
        except:
            return False, open_id
            pass
    else:
        return False, open_id



