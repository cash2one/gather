#! /usr/bin/env python
#! -*- coding: utf-8 -*-

import logging
import traceback

from django.conf import settings

from qiniu import Auth
from qiniu import put_file

access_key = settings.QN_AK
secret_key = settings.QN_SK
bucket_name = settings.BUCKET_NAME

ERROR_LOG = logging.getLogger('err')


class Qiniu(object):

    def get_token(self):
        try:
            q = Auth(access_key, secret_key)
            key = 'jacsicee'
            token = q.upload_token(bucket_name, key)
            return {'result': True, 'token': token}
        except Exception:
            ERROR_LOG.error(traceback.format_exc())
            return {'result': False}

    def upload(self, image_name):
        try:
            q = Auth(access_key, secret_key)
            token = q.upload_token(bucket_name, image_name)
            mime_type = 'image/*'
            localfile = '../media/{image_name}'.format(image_name=image_name)
            ret, info = put_file(token, image_name, localfile, mime_type=mime_type, check_crc=True)
            return {'result': True, 'token': token}
        except Exception:
            ERROR_LOG.error(traceback.format_exc())
            return {'result': False}
