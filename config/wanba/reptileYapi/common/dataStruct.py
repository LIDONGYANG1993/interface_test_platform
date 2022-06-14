#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2021/8/16
# @Name  : 杨望宇

# import requests
import json
import time


class dataStruct:
    class interFace:
        # 接口信息，为None时，表示无法解析页面，需要确认页面
        interface_id = 0  # 接口id
        name = ''  # 名称
        reporter = ''  # 开发者
        status = ''  # 开发状态
        path = ''  # url路径
        method = ''  # 请求方法
        up_time = ''  # 时间戳，更新时间
        add_time = ''  # 时间戳，创建时间
        headers = {}  # 请求头
        body = {}  # 请求参数
        result = {}  # 响应数据
        documentUrl = ''  # 文档地址
        project_id = 0  # 所属项目id
        cat_id = 0  # 所属分类id
        insert_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    class cat:
        # 分类信息
        cat_id = 0  # 分类id
        name = ''  # 名称条目
        desc = ''  # 描述
        up_time = ''  # 时间戳，更新时间
        add_time = ''  # 时间戳，创建时间
        group_id = 0  # 所属组id
        project_id = 0  # 所属项目id
        is_update = False  # 是否存在更新

    class project:
        # 项目信息
        project_id = 0  # 所属项目id
        name = ''  # 名称条目
        desc = ''  # 描述
        up_time = ''  # 时间戳，更新时间
        add_time = ''  # 时间戳，创建时间
        group_id = 0  # 所属组id
        is_update = False  # 是否存在更新

    class group:
        # 组织信息
        group_id = 0  # 所属组id
        name = ''  # 名称条目
        desc = ''  # 描述
        up_time = ''  # 时间戳，更新时间
        add_time = ''  # 时间戳，创建时间
        is_update = False  # 是否存在更新

    class case:
        # 接口用例
        interface_id: int = 0  # 所属接口id
        cat_id: int = 0  # 所属类接口
        project_id: int = 0  # 所属类接口
        case_url_path: str = ''  # 接口路径
        case_model: str = ''  #
        interface_name = ''  #
        case_desc: str = ''  # 用例描述
        cover_version: float = 0.0  # 覆盖版本
        params: dict = {}  # 用例参数
