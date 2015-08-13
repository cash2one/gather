#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

import os

from celery import Celery
from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected, SMTPConnectError

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context, loader

from qn import Qiniu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gather.settings')

app = Celery('gather')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


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


@app.task(bind=True)
def get_image_info(self, image_name):
    q = Qiniu()
    q.get_image_info(image_name)
    return True
