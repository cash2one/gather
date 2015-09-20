#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import socket
import urllib
import base64
import time
import random
import requests
import traceback
import simplejson as json
from datetime import datetime
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
from wechat.forms import WeBindEmailForm
from trade.models import Account
from accounts.models import UserProfile, SMSVerificationCode
from loans.models import AutoInvest

from utils import gen_password

WE_URL_EXPIRE = 5 * 60
WE_USER_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=kker&openid=%s&lang=zh_CN'
WE_GET_ACCESS_TOKEN = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
WE_WEB_GRANT = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=123#wechat_redirect"
WE_LOGIN_ID = '777'


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
                "name": "我的账户",
                "type": "click",
                # "url": WE_WEB_GRANT % (APPID, SERVER_URL + '/accounts/m/account/')
                "key": "ACCOUNT",
            },
        ]
    }
    return requests.post(url, data=json.dumps(params, ensure_ascii=False).encode('utf-8'))


def get_QR_ticket_info(scene_id, temp=True, extra=None):
    """ 获取二维码ticket"""
    url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s' % get_server_access_token()
    if temp:
        params = {
            'expire_seconds': 1800,
            'action_name': 'QR_SCENE',
            'action_info': {
                'scene': {
                    'scene_id': scene_id,
                }
            }
        }
    else:
        params = {
            'action_name': 'QR_LIMIT_SCENE',
            'action_info': {
                'scene': {
                    'scene_id': scene_id,
                }
            }
        }
        if extra:
            params['action_info']['scene'].update(extra)
    r = requests.post(url, data=json.dumps(params))
    return r.json()


def get_QR(ticket):
    """ 获取二维码"""
    url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s' % ticket
    r = requests.get(url)
    return r


def hack_fileobject_close():
    if getattr(socket._fileobject.close, '__hacked__', None):
        return
    old_close = socket._fileobject.close

    def new_close(self, *p, **kw):
        try:
            return old_close(self, *p, **kw)
        except:
            pass
    new_close.__hacked__ = True
    socket._fileobject.close = new_close
hack_fileobject_close()


def verification(request):
    """ 微信验证"""
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')

    temp = sorted([settings.SERVER_TOKEN, timestamp, nonce])
    temp = ''.join(temp)

    sha = hashlib.sha1(temp)
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


def is_login_msg(msg):
    return msg['MsgType'] == 'event' and msg['EventKey'] == WE_LOGIN_ID


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
    bind_email_url = settings.SERVER_URL + "/accounts/m/bind_already_user/?open_id=%s" % open_id

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
            subscribe_time=datetime.fromtimestamp(int(user_info['subscribe_time'])),
            is_subscribed=True,
            is_binded=False,
        ).save()
        return response_text_msg(msg, u'欢迎登录乡信！乡信网站用户请先<a href=\"' + unicode(bind_email_url) + u'\">绑定已有帐号</a>或点击下方"我的账户"注册')
    else:
        profile = WeProfile.objects.get(open_id=open_id)
        if profile.is_binded:
            return response_text_msg(msg, u'欢迎关注乡信微信平台')
        else:
            return response_text_msg(msg, u'欢迎登录乡信！乡信网站用户请先<a href=\"' + unicode(bind_email_url) + u'\">绑定已有帐号</a>或点击下方"我的账户"注册')


def handle_login_msg(msg):
    """ 处理用户扫描登录事件"""
    try:
        open_id = msg['FromUserName']
        bind_email_url = settings.SERVER_URL + "/accounts/m/bind_already_user/?open_id=%s" % open_id
        reset_init_pwd_url = settings.SERVER_URL + "/accounts/m/reset_init_pwd/?open_id=%s" % open_id

        if not WeLoginQR.objects.filter(ticket=msg['Ticket'], is_used=False).exists():
            WeLoginQR(
                ticket=msg['Ticket'],
                open_id=msg['FromUserName'],
                is_used=False,
            ).save()
        if WeProfile.objects.filter(open_id=open_id, is_binded=True).exists():
            return response_text_msg(msg, u'您已通过扫码登录!')

        elif WeProfile.objects.filter(open_id=open_id, is_binded=False, user=None).exists():
            user, pwd = create_user()        
            return response_text_msg(msg, u'您的账号为%s,请尽快<a href=\"' % user.username + unicode(reset_init_pwd_url) + u'\">重置初始密码</a>; 感谢关注乡信！如果您为乡信网站用户, 请先<a href=\"' + unicode(bind_email_url) + u'\">绑定已有帐号</a>')

        elif not WeProfile.objects.filter(open_id=open_id).exists():
            user, pwd = create_user()
            user_info = get_userinfo_server_token(open_id)
            WeProfile(
                user=user,
                username=user.username,
                open_id=user_info['openid'],
                nick_name=user_info['nickname'],
                sex=user_info['sex'],
                language=user_info['language'],
                city=user_info['city'],
                province=user_info['province'],
                country=user_info['country'],
                headimgurl=user_info['headimgurl'],
                subscribe_time=datetime.fromtimestamp(int(user_info['subscribe_time'])),
                is_subscribed=True,
                is_binded=True,
            ).save()
            return response_text_msg(msg, u'您的账号为%s,请尽快<a href=\"' % user.username + unicode(reset_init_pwd_url) + u'\">重置初始密码</a>; 感谢关注乡信！如果您为乡信网站用户, 请先<a href=\"' + unicode(bind_email_url) + u'\">绑定已有帐号</a>')

        else:
            return response_text_msg(msg, u'感谢关注乡信！乡信网站用户请先<a href=\"' + unicode(bind_email_url) + u'\">绑定已有帐号</a>或点击下方"我的账户"注册')
    except:
        print traceback.format_exc()

def create_user():
    user_last = User.objects.filter(username__contains='xiangxin').order_by('-username')[:1].get()

    username = 'xiangxin' + str(int(user_last.username[8:]) + 1)
    pwd = gen_password()
    user = User(
        username=username,
        is_active=True,
    )
    user.save()
    user.set_password(pwd)

    UserProfile(
        user=user,
        username=username,
        nickname=username,
    ).save()

    account = Account(
        user=user,
        ext='微信扫码创建',
    )
    account.save()

    AutoInvest(
        user=user,
        account=account,
        is_active=True,
        active_time=datetime.now(),
    ).save()

    SMSVerificationCode(
        user=user,
    ).save()

    return user, pwd


def wechat_msg(request):
    """ 微信的消息推送"""
    if verification(request):
        data = request.body
        msg = parse_msg(data)
        if user_subscribe_event(msg):
            return handle_subscribe_msg(msg)
        elif is_login_msg(msg):
            return handle_login_msg(msg)
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
    if not we_user.is_binded:
        create_accounts_url = u'\"%s/wechat/create_accounts/?id=%s\"' % (settings.SERVER_URL, encrypt_id)
        bind_email_url = u'\"%s/wechat/bind_email/?id=%s&i=1\"' % (settings.SERVER_URL, encrypt_id)
        return response_text_msg(msg, u'<a href=' + create_accounts_url + u'>创建新帐号</a>\n或者\n' + u'<a href=' + bind_email_url +
                                 u'>绑定已有的乡信帐号></a>')
    else:
        bind_email_url = u'\"%s/wechat/bind_email/?id=%s&i=2\"' % (settings.SERVER_URL, encrypt_id)
        return response_text_msg(msg, u'<a href=' + bind_email_url + u'>重新绑定乡信帐号</a>')


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


def bind_email(request, form_class=WeBindEmailForm, template_name='wechat/bind.html'):
    """ 微信绑定已有的乡信帐号"""
    open_id = None
    bind_type = None
    if request.method == 'POST':
        form = form_class(request, data=request.POST)
        if form.is_valid():
            bind_type = int(form.cleaned_data['bind_type'])
            open_id = form.cleaned_data['open_id']
            we_profile = WeProfile.objects.get(open_id=open_id)
            if bind_type == 1:
                # 第一次绑定
                old_user = we_profile.user
                new_user = User.objects.get(username=form.cleaned_data['username'])
                we_profile.user = new_user
                we_profile.username = new_user.username
                we_profile.is_binded = True
                we_profile.save()
                old_user.is_active = False
                old_user.save()
            else:
                new_user = User.objects.get(username=form.cleaned_data['username'])
                we_profile.user = new_user
                we_profile.username = new_user.username
                we_profile.save(force_update=True)
            return HttpResponseRedirect('/')
    else:
        form = form_class(request)
        open_id = request.GET['id']
        bind_type = request.GET['i']
    return render(request, template_name, {
        'form': form,
        'open_id': open_id,
        'bind_type': bind_type,
    })


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


def oauth(request):
    """ """
    pass


def we_auto_login(func):
    """ 用户点击view菜单，自动登录的修饰器"""
    def wrap(request, *args, **kwargs):
        open_id = request.GET.get('open_id')
        try:
            if not request.user.is_authenticated():
                from django.contrib.auth import login
                we_profile = WeProfile.objects.get(open_id=open_id, is_binded=True)
                user = authenticate(remote_user=we_profile.user.username)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
        except WeProfile.DoesNotExist:
            if WeProfile.objects.filter(open_id=open_id, is_binded=False).exists():
                return HttpResponseRedirect('%s?open_id=%s' % (reverse('accounts.mviews.bind_already_user'), open_id))
            else:
                return HttpResponseRedirect(reverse('accounts.mviews.register_mobile'))

            return HttpResponseRedirect('%s?open_id=%s' % (reverse('accounts.mviews.login'), open_id))

        return func(request, *args, **kwargs)
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def code_get_openid(request):
    """ 通过auth的code获取open_id"""
    code = request.GET.get('code', '')
    open_id = None
    if code:
        params = {
            'appid': settings.APPID,
            'secret': settings.APPSECRET,
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
    else:
        return False, open_id


def we_login(request):
    """ 微信扫描登录"""
    web_ticket = request.GET['ticket']
    we_ticket = urllib.unquote(web_ticket)
    try:
        login_qr = WeLoginQR.objects.get(ticket=we_ticket, is_used=False)
    except WeLoginQR.DoesNotExist:
        d = {
            'res': 'no',
            'msg': 'no_ticket'
        }
        return HttpResponse(json.dumps(d))
    try:
        we_profile = WeProfile.objects.get(open_id=login_qr.open_id)
    except WeProfile.DoesNotExist:
        d = {
            'res': 'no',
            'msg': 'no_profile'
        }
        return HttpResponse(json.dumps(d))
    user = authenticate(remote_user=we_profile.user.username)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    login_qr.is_used = True
    login_qr.save()

    d = {
        'res': 'ok',
        'path': reverse('wei.views.account'),
    }
    return HttpResponse(json.dumps(d))


def web_get_ticket(request):
    """ 网页获取ticket"""
    ticket_type = request.GET.get('type', None)
    ticket = get_QR_ticket_info(ticket_type).get('ticket', '')
    if ticket:
        d = {
            'ticket': ticket,
            'success': True,
        }
    else:
        d = {
            'ticket': '',
            'success': False,
        }
    return HttpResponse(json.dumps(d))


def web_get_QR(request):
    """ 网页获取二维码"""
    ticket = request.GET['ticket']
    r = get_QR(ticket)
    return HttpResponse(r.content, 'image/jpg')


def create_accounts(request):
    """ 由微信创建帐号"""
    encrypt_id = request.GET.get('id', '')
    if not encrypt_id:
        return HttpResponse('参数错误')
    try:
        value = base64.b64decode(encrypt_id)
        try:
            signer = TimestampSigner()
            open_id = signer.unsign(value)
        except SignatureExpired:
            return HttpResponse('链接已失效')
    except:
        return HttpResponse('参数错误')

    we_user = WeProfile.objects.get(open_id=open_id)
    user = we_user.user
    username = user.username
    password = str(random.randrange(100000, 999999))
    user.set_password(password)
    user.save()
    content = u'您的用户名：%s,密码：%s' % (username, password)
    send_msg(open_id, content)
    return HttpResponse(content)
