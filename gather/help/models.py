#!/usr/bin/python
#-*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Help(models.Model):
    """ 书签信息"""
    user = models.ForeignKey(User, related_name='helps')
    
