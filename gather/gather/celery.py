#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

import os
import requests
import simplejson as json
import logging

from celery import Celery
from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected, SMTPConnectError

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context, loader

from wechat.models import WeProfile
from wechat.views import get_server_access_token
from utils import gen_info_msg

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gather.settings')

app = Celery('gather')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

INFO_LOG = logging.getLogger('info')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    return 'done'


@app.task(bind=True)
def async_send_mail(self, subject, message, recipient_list):
    """ 发送邮件"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return True, ''
    except SMTPRecipientsRefused:
        return False, '邮箱不存在'


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def async_send_html_email(self, subject, recipient_list, template_name, context):
    """ 发送html邮件"""
    try:
        t = loader.get_template(template_name)
        msg = EmailMultiAlternatives(subject, t.render(Context(context)), settings.DEFAULT_FROM_EMAIL, recipient_list)
        msg.content_subtype = 'html'
        msg.send()
        return True, ''
    except (SMTPServerDisconnected, SMTPConnectError) as exc:
        self.retry(exc)
    except SMTPRecipientsRefused:
        return False, '邮箱不存在'


#@app.task(bind=True, default_retry_delay=300, max_retries=1)
def send_wechat_msg(user, msg_type, order_id, data=None):
    open_id = WeProfile.objects.get(user=user).open_id

    if msg_type == 'order_create':
        template_id = settings.ORDER_CREATE_ID
    elif msg_type == 'order_get':
        template_id = settings.ORDER_UPDATE_ID
    elif msg_type == 'order_post':
        template_id = settings.ORDER_UPDATE_ID
    elif msg_type == 'order_succ':
        template_id = settings.ORDER_UPDATE_ID
    elif msg_type == 'order_close':
        template_id = settings.ORDER_CLOSE_ID

    json_data = {
       "touser": str(open_id),
       "template_id": template_id,
       "url":  "{url}/wash/user/order/detail/{order_id}".format(url=settings.SERVER_NAME, order_id=order_id),
       "data": data
    }
    access_token = get_server_access_token()
    url = settings.SEND_WE_MSG_URL % access_token
    r = requests.post(url, json.dumps(json_data, ensure_ascii=False).encode('utf-8'))


