#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/30
# @Name  : 杨望宇


# app request请求
import json
import requests

from case_plan.core.data import tokenData
from case_plan.models import tokenModel
from config.wanba.privateServer import privateInterFace

def app_request(case_url, params,environment, cookies=None):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    if 'http' in case_url:
        r = requests.post(case_url, data=params, headers=headers, verify=False)
    elif case_url.split('/')[1] == 'v3':
        data = {
            'url': case_url,
            'params': json.dumps(params, ensure_ascii=False)
        }
        r = requests.post(url=environment["value"]["url_api"], data=data, headers=headers, cookies=cookies)
    elif case_url.split('/')[1] == 'web':
        data = {
            'url': case_url,
            'params': json.dumps(params, ensure_ascii=False)
        }
        r = requests.post(url=environment["value"]["url_webapi"], data=data, headers=headers, cookies=cookies)
    else:
        data = {
            'url': case_url.split('/')[1],
            'params': json.dumps(params),
            'host': 'intimacy.wb-ms.com'
        }
        r = requests.post(url=environment["value"]["url_ms"], data=data, headers=headers, cookies=cookies)
    return r


def assert_token_test(uid, environment):
    params = {"uid": uid, "uidStr": str(uid)}
    path = "/v3/user/basic/userInfo"
    res = app_request(path, params, environment).json()
    if res["code"] == 0:
        return True
    return False

def get_new_and_save_token(token, uid, environment, appType, ticket):
    token.uid = uid
    token.environment = environment
    token.appType = appType
    token.token = ticket
    token.save()
    return True

def get_token_test(uid,environment,appType, server):
    try:
        token = tokenData(uid=uid, environment=environment, app_type=appType).model_data
    except Exception as e:
        token = tokenModel.objects.create(uid=uid, environment=environment,app_type=appType, token=None)
    try:
        token.token = server.getTicket(uid, uid, uid, isTest=True).json()["data"]
        if not assert_token_test(uid, environment):
            return False,None
        token.save()
        return True, token.token
    except Exception as e:
        return False,None

def get_token(params, environment):
    if not params: return None
    uid = params.get("uid", None)
    if not uid: return None
    server = privateInterFace()
    if environment["value"]["appType"] == "main" and environment["value"]["environment"] == "test":
        _, token = get_token_test(uid, environment["value"]["appType"], environment["value"]["environment"], server)
        if _:
            return token
    return None
