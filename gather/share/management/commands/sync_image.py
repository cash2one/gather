#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import traceback

from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from share.models import Share

from qn import Qiniu


INFO_LOG = logging.getLogger('info')
ERROR_LOG = logging.getLogger('err')


class Command(BaseCommand):

    help = u'同步图片到七牛'

    option_list = BaseCommand.option_list + (
        make_option('-s', '--sync',
            action='store',
            dest='sync',
            default=True,
            help='sync image'
        ),
    )

    def handle(self, *args, **options):
        try:
            if options['sync']:
                q = Qiniu()
                shares = Share.objects.filter(photo__contains='.').order_by('-created')
                for share in shares:
                    q.upload(share.photo.name)
        except Exception:
            ERROR_LOG.error(traceback.format_exc())

