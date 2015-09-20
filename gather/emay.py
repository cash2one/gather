#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import traceback
import requests
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException
from xml.etree import ElementTree

EMAY_LOG = logging.getLogger('emay')

class Emay(object):

    def __init__(self):
        self.cdkey = '9SDK-EMY-0229-JDQUK'
        self.passowrd = 'df311175c5040abf3f6d79d5203afeda'
        self.url = 'http://sdk229ws.eucp.b2m.cn:8080/sdkproxy/sendsms.action'

    def send(self, phones, msg):
        params = {
            'cdkey': self.cdkey,
            'password': self.passowrd,
            'phone': ','.join(phones),
            'message': msg,
            'addserial': '',
        }
        url = self.url + '?cdkey=%(cdkey)s&password=%(password)s&phone=%(phone)s&message=%(message)s&addserial=' % params
        try:
            rsp = requests.get(url)
            xml = ET.fromstring(rsp.content.strip())
            data = 'phones=%s, msg=%s, error=%s, message=%s' % (phones, msg, xml.find('error').text, xml.find('message').text)
            EMAY_LOG.info(data)
            return True
        except RequestException as e:
            EMAY_LOG.error(traceback.format_exc())
            raise e
            return False


def test():
    emay = Emay()
    emay.send(['15652191547', '18001296696'], "韩总是写代码的")


if __name__ == '__main__':
    test()
