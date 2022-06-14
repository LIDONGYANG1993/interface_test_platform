#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/06/16
# @Name  : 杨望宇

import requests
import json
from config.yapi_config import yapi_name, yapi_pwd

def yapi_login():
    url = "http://ops-api.wb-intra.com/api/v1/login"
    data = {
        "password": yapi_pwd,
        "username": yapi_name
    }
    res = requests.post(url, json=data)
    res_json = json.loads(res.text)
    yapiOperatorName = res_json['resp']['info']['username']
    yapiToken = res_json['resp']['token']
    user_token = {
        "yapiOperatorName": yapiOperatorName,
        "yapiLdapToken": yapiToken
    }
    return user_token
