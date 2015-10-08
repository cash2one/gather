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
    
    #online
    #AccountSid='8a48b5514700da2f01471919c13c0618'
    #AccountToken='40d4cbc29e7a4a55a548c685993fa7cc'
    #AppId='8a48b55148874bfb01488c85bec101f4'

    #test
    AccountSid = '8a48b5514fd49643014fd59022a804c9'
    AccountToken = '8de3a7195bd14fd991b320eb771fead9'
    AppId = 'aaf98f894fd44d15014fd59e8a1202f9'
    
    SubAccountSid=''
    SubAccountToken=''
    VoIPAccount=''
    VoIPPassword=''
    #ServerIP='app.cloopen.com'

    ServerIP = 'sandboxapp.cloopen.com'
    ServerPort = '8883'
    SoftVersion = '2013-12-26'
    Iflog = True #是否打印日志
    Batch = ''  #时间戳
    BodyType = 'json'#包体格式，可填值：json 、xml
    
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

        if  settings.DEBUG == True:
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

def test():
    rest = REST()
    result = rest.voice_verify('123456', '18510912695')
    print result

if __name__ == '__main__':
    test()

