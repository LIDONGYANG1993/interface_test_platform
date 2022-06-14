#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/30
# @Name  : 杨望宇


# app request请求
import json
from urllib import parse

import requests

from case_plan.core.data import tokenData
from case_plan.models import tokenModel
from config.wanba.privateServer import privateInterFace
from config.wanba.yapi_login import yapi_login


# 玩吧内部的接口请求，仅在内网调用
def app_request(case_url, params, environment, cookies=None):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'url': case_url,
        'params': json.dumps(params, ensure_ascii=False)
    }
    if environment["value"]["environment"] == "product":
        params.update({"deviceId": "7892BD2B-23A4-4520-A1FD-69642CF5F5A8"})
        data.update(yapi_login())
        data.update(params)
        data.update({"params":json.dumps(params)})
    if case_url.split('/')[1] == 'v3' or case_url.split('/')[1] == 'v2':
        url = environment["value"]["url_api"]
    elif case_url.split('/')[1] == 'web':
        url = environment["value"]["url_webapi"]
    else:
        url = environment["value"]["url_rpc"]
    r = requests.post(url=url, data=data, headers=headers, cookies=cookies)
    return r


#  验证token方法，依赖/v3/user/basic/userInfo接口，当该接口失效或者删除时，需要修改
def assert_token(uid, environment):
    if api_ticket_assert(uid, environment) and web_ticket_assert(uid, environment):
        return True
    return False

def api_ticket_assert(uid, environment):
    params = {"uid": uid, "uidStr": str(uid)}
    path = "/v3/user/basic/userInfo"
    res = app_request(path, params, environment).json()
    if "__terror" in res:
        return False
    if res["code"] == 3:
        return False
    return True


def web_ticket_assert(uid, environment):
    params = {"uid": uid}
    path = "/web/webApi/shop/getWebUserCurrency"
    res = app_request(path, params, environment).json()
    if "__terror" in res:
        return False
    if res["code"] == 3:
        return False
    return True

def get_new_and_save_token(token, uid, environment, appType, ticket):
    token.uid = uid
    token.environment = environment
    token.appType = appType
    token.token = ticket
    token.save()
    return True


def get_token_test(uid, environment, server):
    token = create_token_data(uid, environment)
    try:
        # 尝试验证token，如果验证失败，重新生成token并保存在库里
        if not token.token or not assert_token(uid, environment):
            token.token = server.getTicket(uid, uid, uid, isTest=True).json()["data"]
            token.save()
            return True, token.token
        return True, token.token
    except Exception:
        return False, None

def get_token_product(uid,user,pwd, environment, server):
    if not (uid and user, pwd):
        return False, None
    token = create_token_data(uid, environment)
    try:
        # 尝试验证token，如果验证失败，重新生成token并保存在库里
        if not token.token or not assert_token(uid, environment):
            r = server.getTicket(uid, user, pwd, isTest=False)
            token.token = r.json()["data"]
            token.save()
            return True, token.token
        return True, token.token
    except Exception as e:
        return False, None


def create_token_data(uid, environment):
    try:  # 尝试从数据库获取token 如果没获取到， 创建一个新的token记录
        token = tokenData(uid=uid, environment=environment["value"]["environment"], app_type=environment["value"]["appType"]).model_data
    except Exception as e:
        token = tokenModel.objects.create(uid=uid, environment=environment["value"]["environment"],app_type=environment["value"]["appType"], token=None)
    return token

#  从对应环境中获取
def get_token(params, environment):
    if not params: return None
    uid = params.get("uid", None)
    username = params.get("username", None)
    password = params.get("password", None)
    if not uid: return None
    server = privateInterFace()
    _, token = None,None
    if environment["value"]["appType"] == "main" and environment["value"]["environment"] == "test":
        _, token = get_token_test(uid, environment, server)
    if environment["value"]["appType"] == "main" and environment["value"]["environment"] == "product":
        _, token = get_token_product(uid,username, password, environment, server)
    if _:
        return token
    return None


def login_yapi():
    pass
