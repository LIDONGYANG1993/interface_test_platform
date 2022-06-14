#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2021/8/16
# @Name  : 杨望宇
from config.yapi_config import host_yapi
import json
import time

import requests
from config.wanba.reptileYapi.common.dataStruct import dataStruct


def class_to_dict(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            pr[name] = value
    return pr


def get(url, body, headers=None):
    res = requests.get(url=url, params=body, headers=headers)
    assert res.status_code == 200
    assert res.json()['errcode'] == 0
    return res


def post(url, body, headers=None):
    res = requests.post(url=url, data=body, headers=headers)
    assert res.status_code == 200
    assert res.json()['errcode'] == 0
    return res


def _request(url, body, method, headers=None):
    res = None
    if method.upper() == 'POST':
        res = requests.post(url=url, data=body, headers=headers)
    if method.upper() == 'GET':
        res = requests.get(url=url, params=body, headers=headers)
    assert res.status_code == 200
    assert res.json()['errcode'] == 0
    return res

def version_set(timeStamp):
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y%m%d%H%M%S", timeArray)
    return 'ver' + otherStyleTime



class yapiInformation:

    def __init__(self, user=None, password=None):
        self.host = host_yapi
        self.url = self.host + '{}'
        self.yapiUrl = 'http://yapi.wb-intra.com/project/{}/interface/api/{}'
        self.user = user
        self.password = password
        self.errors = []
        self.headers = self.build_headers()

    def post(self, url, body, headers=None):
        try:
            return _request(url, body, 'POST', headers)
        except AssertionError as e:
            self.errors.append(dict(url=url, params=body, error=e))
            return None

    def get(self, url, body, headers=None):
        try:
            return _request(url, body, 'GET', headers)
        except AssertionError as e:
            self.errors.append(dict(url=url, params=body, error=e))
            return None

    @staticmethod
    def read_headers(req_headers: list):
        res = {}
        try:
            for rel in req_headers:
                res.update({rel['name']: rel['value']})
        except Exception as e:
            return None
        return res

    @staticmethod
    def read_params(body_str: str):
        try:
            res = json.loads(body_str)
        except Exception as e:
            return None
        return res

    @staticmethod
    def read_params_list(body_list: list):
        res = {}
        for body in body_list:
            res[body["name"]] = {"type":body["type"], "desc":body["desc"]}
        return {"properties":res}

    @staticmethod
    def dict_key_get(key, _dict):
        if _dict.__contains__(key):
            return _dict[key]
        else:
            return None

    # 登录获取cookie
    def login(self):
        url = self.url.format('/api/user/login_by_ldap')
        body = dict(
            email=self.user,
            password=self.password
        )
        res = post(url, body)
        con1 = res.cookies['_yapi_token']
        con2 = res.cookies['_yapi_uid']
        return '_yapi_token={0}; _yapi_uid={1}'.format(con1, con2)

    def build_headers(self):
        return {
            'Cookie': self.login(),
            'Content-T': 'application/json'
        }

    # 获取全部组
    def get_groups(self):
        list_group = []
        project = self._get_groups()
        for rel in project.json()['data']:
            _group = self._group_class(rel)
            if _group.name == '个人空间':
                continue
            list_group.append(class_to_dict(_group))
        return list_group

    # 获取单个group
    def get_group(self, group_id):
        group = None
        project = self._get_groups()
        for rel in project.json()['data']:
            _group = self._group_class(rel)
            if _group.name == '个人空间':
                continue
            if _group.group_id == group_id:
                return _group
        return None

    # 获取组内全部项目
    def _get_groups(self):
        url = self.url.format('/api/group/list')
        body = dict()
        res = self.get(url, body, self.headers)
        return res

    def _group_class(self, group_req):
        r_project = dataStruct.project()
        r_project.group_id = self.dict_key_get('_id', group_req)
        r_project.name = self.dict_key_get('group_name', group_req)
        r_project.desc = self.dict_key_get('group_desc', group_req)
        r_project.up_time = self.dict_key_get('up_time', group_req)
        r_project.add_time = self.dict_key_get('add_time', group_req)
        return r_project

    # 获取组内全部项目
    def get_projects(self, groupId):
        list_project = []
        project = self._get_projects(groupId)
        for rel in project.json()['data']['list']:
            list_project.append(class_to_dict(self._project_class(rel)))
        return list_project

    def _project_class(self, project_req: dict):
        r_project = dataStruct.project()
        r_project.project_id = self.dict_key_get('_id', project_req)
        r_project.name = self.dict_key_get('name', project_req)
        r_project.desc = self.dict_key_get('desc', project_req)
        r_project.up_time = self.dict_key_get('up_time', project_req)
        r_project.add_time = self.dict_key_get('add_time', project_req)
        r_project.group_id = self.dict_key_get('group_id', project_req)
        return r_project

    def _get_projects(self, groupId):
        page = 1
        limit = 200
        url = self.url.format('/api/project/list')
        body = dict(group_id=groupId,
                    page=page,
                    limit=limit,
                    )
        res = self.get(url, body, self.headers)
        return res

    # 获取项目内全部分类
    def get_cats(self, projectId):
        _cat = dataStruct.cat()
        list_cat = []
        pro = self._get_project(projectId)
        group_id = self.dict_key_get('group_id', pro.json()['data'])
        if pro:
            for rel in pro.json()['data']['cat']:
                _cat = self._cat_class(rel)
                _cat.group_id = group_id
                cat = class_to_dict(_cat)
                list_cat.append(cat)
        return list_cat

    def _cat_class(self, cat_req: dict) -> object:
        r_cat = dataStruct.cat()
        r_cat.cat_id = self.dict_key_get('_id', cat_req)
        r_cat.name = self.dict_key_get('name', cat_req)
        r_cat.desc = self.dict_key_get('desc', cat_req)
        r_cat.up_time = self.dict_key_get('up_time', cat_req)
        r_cat.add_time = self.dict_key_get('add_time', cat_req)
        r_cat.project_id = self.dict_key_get('project_id', cat_req)
        return r_cat

    def _get_project(self, projectId):
        url = self.url.format('/api/project/get')
        body = dict(id=projectId, )
        res = self.get(url, body, self.headers)
        return res

    # 获取当前分类的所有接口信息
    def get_interfaces_for_cat(self, catId):
        return self._get_interfaces_for_cat_all(catId)

    def yield_interfaces_for_cat(self, catId):
        yield self._get_interfaces_for_cat_all(catId)

    # 获取整个项目所有接口信息
    def get_interfaces_for_project(self, projectId):
        return self._get_interfaces_for_project_all(projectId)


    def yield_interfaces_for_project(self, projectId):
        cat = self.get_cats(projectId)
        for rel in cat:
            yield self._get_interfaces_for_cat_all(rel['cat_id'])

    # 获取整组的所有接口信息
    def get_interfaces_for_group(self, groupId):
        interfaces = []
        group_list = self.get_projects(groupId)
        for rel in group_list:
            interfaces = interfaces + self.get_interfaces_for_project(projectId=rel['project_id'])
        return interfaces

    def yield_interfaces_for_group(self, groupId):
        group_list = self.get_projects(groupId)
        for rel in group_list:
            yield self.yield_interfaces_for_project(projectId=rel['project_id'])

    # 内部方法
    def _get_interfaces_for_cat_all(self, catId, page=1, limit=100, interfaces=None):
        if interfaces is None:
            interfaces = []
        url = self.url.format('/api/interface/list_cat')
        body = dict(catid=catId,
                    page=page,
                    limit=limit,
                    )
        res = get(url, body, self.headers).json()
        for rel in res['data']['list']:
            interfaces.append(self.get_interface(rel['_id']))
        if page == res['data']['total'] or 0 == res['data']['count']:
            return interfaces
        else:
            return self._get_interfaces_for_cat_all(catId, page + 1, limit, interfaces)

    # 内部方法
    def _get_interfaces_for_project_all(self, projectId, page=1, limit=100, interfaces=None):
        if interfaces is None:
            interfaces = []
        url = self.url.format('/api/interface/list')
        body = dict(project_id=projectId,
                    page=page,
                    limit=limit,
                    )
        res = get(url, body, self.headers).json()
        for rel in res['data']['list']:
            interfaces.append(self.get_interface(rel['_id']))
        if page == res['data']['total']:
            return interfaces
        else:
            return self._get_interfaces_for_project_all(projectId, page + 1, limit, interfaces)

    # 获取单页的接口信息
    def get_interfaces_for_project_page(self, projectId, page, limit):
        interfaces = []
        url = self.url.format('/api/interface/list')
        body = dict(project_id=projectId,
                    page=page,
                    limit=limit,
                    )
        res = get(url, body, self.headers).json()
        for rel in res['data']['list']:
            interfaces.append(self.get_interface(rel['_id']))
        return interfaces

    # 获取单个接口信息
    def get_interface(self, _id):
        url = self.url.format('/api/interface/get')
        body = dict(id=_id)
        res = get(url, body, self.headers).json()['data']

        _interface = dataStruct.interFace()
        _interface.interface_id = self.dict_key_get('_id', res)
        _interface.cat_id = self.dict_key_get('catid', res)
        _interface.project_id = self.dict_key_get('project_id', res)
        _interface.documentUrl = self.yapiUrl.format(_interface.project_id, _interface.interface_id)
        _interface.name = self.dict_key_get('title', res)
        _interface.reporter = self.dict_key_get('username', res)
        _interface.status = self.dict_key_get('status', res)
        _interface.up_time = self.dict_key_get('up_time', res)
        _interface.add_time = self.dict_key_get('add_time', res)
        _interface.path = self.dict_key_get('path', res)
        _interface.method = self.dict_key_get('method', res)
        if res.__contains__('res_body'):
            _interface.result = self.read_params(res['res_body'])
        if res.__contains__('req_body_other'):
            _interface.body = self.read_params(res['req_body_other'])
        elif res.__contains__('req_body_form'):
            _interface.body = self.read_params_list(res['req_body_form'])
        if res.__contains__('req_headers'):
            _interface.headers = self.read_headers(res['req_headers'])
        res_interface = class_to_dict(_interface)
        return res_interface


if __name__ == '__main__':
    y = yapiInformation(user='yangwangyu', password='Yang840251')  # 初始化数据，需要yapi账户密码
    interfaces_group = y.get_interfaces_for_group(groupId=1085)  # 获取组内所有项目的接口信息
    interfaces_project = y.get_interfaces_for_project(projectId=230)  # 获取项目内所有接口信息
    interfaces_cat = y.get_interfaces_for_cat(catId=1327)  # 获取某一个分类，所有接口信息
    interface = y.get_interface(_id=2511)  # 获取某一个接口的信息
    groups = y.get_groups()  # 获取所有项目组
    projects = y.get_projects(groupId=360)  # 获取组内所有项目
    cats = y.get_cats(projectId=230)  # 获取项目内所有分类
