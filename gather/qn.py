#! /usr/bin/env python
#! -*- coding: utf-8 -*-

import logging
import traceback
import requests

from django.conf import settings

from qiniu import Auth, BucketManager
from qiniu import put_file, put_data
from share.models import ip_proxy

access_key = settings.QN_AK
secret_key = settings.QN_SK
bucket_name = settings.BUCKET_NAME

ERROR_LOG = logging.getLogger('err')


class Qiniu(object):

    def get_token(self, key='jacsicee'):
        try:
            q = Auth(access_key, secret_key)
            token = q.upload_token(bucket_name, key)
            return {'result': True, 'token': token}
        except Exception:
            ERROR_LOG.error(traceback.format_exc())
            return {'result': False}

    def upload(self, image_name):
        try:
            token = self.get_token(image_name)['token']
            mime_type = 'image/*'
            localfile = '../media/{image_name}'.format(image_name=image_name)
            ret, info = put_file(token, image_name, localfile, mime_type=mime_type, check_crc=True)
            return {'result': True, 'token': token}
        except Exception:
            ERROR_LOG.error(traceback.format_exc())
            return {'result': False}

    def upload_stream(self, image_name, localfile):
        try:
            token = self.get_token(image_name)['token']
            ret, info = put_data(token, image_name, localfile)
        except Exception:
            ERROR_LOG.error(traceback.format_exc())
            return {'result': False}

    def get_image_info(self, image_name):
        ips = ip_proxy.objects.filter(status=1).order_by("-succ_count")
        for ip in ips:
            try:
                proxies = {
                    'http': 'http://{}:{}'.format(ip.ip, ip.port),
                    'https': 'http://{}:{}'.format(ip.ip, ip.port),
                }
                url = "http://7xkqb1.com1.z0.glb.clouddn.com/{}?imageInfo".format(image_name)
                r = requests.get(url, proxies=proxies, timeout=1)
                if r.status_code == 200:
                    width = r.json()['width']
                    height = r.json()['height']
                    return width, height
            except:
                continue


if __name__ == "__main__":
    q = Qiniu()
    print q.get_image_info("1439356387557369085.jpg")
