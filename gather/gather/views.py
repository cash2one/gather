#!/usr/bin/python
#-*- coding: utf-8 -*-

import simplejson as json

from django.shortcuts import render

from config.models import DevelopLog
from django.http import HttpResponse, HttpResponseRedirect


def index(request, template_name='index.html'):
    """ 主页显示"""
    return render(request, template_name, {})


def about_us(request, template_name='about_us.html'):
    """ 关于我"""
    logs = DevelopLog.objects.all().order_by('-created')
    return render(request, template_name, {
        'logs': logs
    })

def check_vin(request):
    vin = request.GET.get('vin', '')
    data = {}
    if vin:
        vin_num = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
            'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        }

        jiaquan = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
        vin_sum = 0

        for i in xrange(17):
            if i != 8:
                try:
                    key = int(vin[i])
                except ValueError:
                    key = vin_num[vin[i]]

                vin_sum += key * jiaquan[i]

        left = vin_sum % 11

        data['vin'] = vin
        data['verify_code'] = vin[8]
        data['vin_sum'] = vin_sum
        data['status'] = str(left) == vin[8]
        return HttpResponse(json.dumps(data))

    return HttpResponse(json.dumps({'result': False}))


