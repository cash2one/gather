#!/usr/bin/python
#-*- coding: UTF-8 -*-

import md5
import base64
import datetime
import urllib2
import logging
import traceback
import simplejson as json

from django.conf import settings

VOICE_LOG = logging.getLogger('voice_verify')


class REST:

    #if settings.DEBUG:
        # test
    ServerIP = 'sandboxapp.cloopen.com'
    #else:
        # online
    #    ServerIP = 'app.cloopen.com'

    AppId = 'aaf98f894fd44d15014fd59e8a1202f9'
    AccountSid = '8a48b5514fd49643014fd59022a804c9'
    AccountToken = '8de3a7195bd14fd991b320eb771fead9'
    SubAccountSid=''
    SubAccountToken=''
    VoIPAccount=''
    VoIPPassword=''

    ServerPort = '8883'
    SoftVersion = '2013-12-26'
    Iflog = True  # 是否打印日志
    Batch = ''  # 时间戳
    BodyType = 'json'  # 包体格式，可填值：json 、xml
    
    def __init__(self):
        self.ServerIP = REST.ServerIP
        self.ServerPort = REST.ServerPort
        self.SoftVersion = REST.SoftVersion
        self.BodyType = REST.BodyType
    
    def setAccount(self):
      self.AccountSid = REST.AccountSid
      self.AccountToken = REST.AccountToken
    
    def setAppId(self, AppId):
       self.AppId = AppId
    
    def voice_verify(self, verify_code, to):

        if settings.DEBUG == True:
            return True
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = md5.new(signature).hexdigest().upper()
        url = "https://"+self.ServerIP + ":" + self.ServerPort + "/" + self.SoftVersion + "/Accounts/" + self.AccountSid + "/Calls/VoiceVerify?sig=" + sig
        src = self.AccountSid + ":" + self.Batch
        auth = base64.encodestring(src).strip()

        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
        req.add_header("Authorization", auth)
        
        body ='''<?xml version="1.0" encoding="utf-8"?><VoiceVerify>\
            <appId>%s</appId><verifyCode>%s</verifyCode><playTimes>%s</playTimes><to>%s</to><respUrl>%s</respUrl>\
            <displayNum>%s</displayNum></VoiceVerify>\
            '''%(self.AppId, verify_code, 2, to, '', '')
        if self.BodyType == 'json':
            body = '''{"appId": "%s", "verifyCode": "%s","playTimes": "%s","to": "%s","respUrl": "%s","displayNum": "%s"}'''%(self.AppId, verify_code, 3, to,'', '')
        req.add_data(body)

        try:
            res = urllib2.urlopen(req)
            data = res.read()
            data_dict = json.loads(data)
            res.close()
            if data_dict['statusCode'] != '000000':
                VOICE_LOG.error("verifyCode=%s, mobile=%s, statusCode=%s, error=%s" % (verify_code, to, data_dict['statusCode'], data_dict['statusMsg']))
                return False
            else:
                VOICE_LOG.info("verifyCode=%s, mobile=%s" % (verify_code, to))
                return True
        except Exception:
            VOICE_LOG.error(traceback.format_exc())
            return False

    # 发送模板短信
    # @param to  必选参数     短信接收彿手机号码集合,用英文逗号分开
    # @param datas 可选参数    内容数据
    # @param tempId 必选参数    模板Id
    def sendTemplateSMS(self, to, datas, tempId):

        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = md5.new(signature).hexdigest().upper()
        # 拼接URL
        url = "https://"+self.ServerIP + ":" + self.ServerPort + "/" + self.SoftVersion + "/Accounts/" + self.AccountSid + "/SMS/TemplateSMS?sig=" + sig
        # 生成auth
        src = self.AccountSid + ":" + self.Batch
        auth = base64.encodestring(src).strip()
        req = urllib2.Request(url)
        self.setHttpHeader(req)
        req.add_header("Authorization", auth)
        # 创建包体
        b = ''
        for a in datas:
            b += '<data>%s</data>' % (a)

        body ='<?xml version="1.0" encoding="utf-8"?><SubAccount><datas>'+b+'</datas><to>%s</to><templateId>%s</templateId><appId>%s</appId>\
            </SubAccount>\
            '%(to, tempId,self.AppId)
        if self.BodyType == 'json':
            # if this model is Json ..then do next code
            b='['
            for a in datas:
                b += '"%s",'%(a)
            b += ']'
            body = '''{"to": "%s", "datas": %s, "templateId": "%s", "appId": "%s"}'''%(to,b,tempId,self.AppId)
        req.add_data(body)
        data=''
        try:
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)

            return locations
        except Exception, error:

            return {'172001': '网络错误'}

    #设置包头
    def setHttpHeader(self,req):
        if self.BodyType == 'json':
            req.add_header("Accept", "application/json")
            req.add_header("Content-Type", "application/json;charset=utf-8")

        else:
            req.add_header("Accept", "application/xml")
            req.add_header("Content-Type", "application/xml;charset=utf-8")


def test():
    rest = REST()
    #result = rest.voice_verify('123456', '18510912695')
    result = rest.sendTemplateSMS('18510912695', [1234, 2], 42221)
    print result

if __name__ == '__main__':
    test()

