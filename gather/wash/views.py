#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson as json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def index(request, template_name='wash/index.html'):
    return render(request, template_name)


def show(request, template_name='wash/show.html'):
    return render(request, template_name)


def account(request, template_name='wash/account.html'):
    return render(request, template_name)
