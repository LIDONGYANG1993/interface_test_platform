#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/02/16
# @Name  : 杨望宇
import json
from config.wanba import *

import requests


class privateInterFace:
    def __init__(self):
        self.host = "http://101.200.239.26:5050{}"
        self.url_ticket = self.host.format("/apiTest/getTicket")
        self.url_updateToken = self.host.format("/checkKnapsack/insertToken")
        self.url_getOnlineToken = self.host.format("/checkKnapsack/getOnlineToken")
        self.url_checkAPi = self.host.format("/apiTest/checkApi")

    def getTicket(self, userName, pwd, uid, isTest=False):
        #  重新创建t票
        if isTest:
            envsType = "3"
        else:
            envsType = "2"
        body = {
            "userName": userName,
            "passWord": pwd,
            "uid": uid,
            "key": keys,
            "envsType": envsType  # 1代表星辰线上，2代表主包线上, 3代表主包测试
        }
        return requests.post(self.url_ticket, data=json.dumps(body), headers=header)


    def updateToken(self, userName: str, token: str, uid: str, envsType):
        #  更新token
        body = {
            "uid": uid,
            "token": token,
            "user": userName,
            "envsType": envsType,
        }
        return requests.post(self.url_updateToken, data=json.dumps(body), headers=header)

    def getOnlineToken(self, userName: str, envsType):
        #  获取保存的token
        body = {
            "user": userName,
            "envsType": envsType
        }
        return requests.get(self.url_getOnlineToken, params=body, headers=header)


if __name__ == '__main__':
    a = privateInterFace().getTicket("liqi123","123456", "1231231",False).json()
    print(a)