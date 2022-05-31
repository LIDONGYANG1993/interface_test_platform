#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json


#  依据路径【path】从字典【dict】中， 有条件的【condition】读取数据， condition 仅在遇到list数据时，传值使用
#  _str: a.b.c  _dict:{"a":{"b":{"c":"157888"}}},  condition： [{"w":"9"},{"z":11}]
import time


def get_path_dict_condition(_str: str, _dict: dict, condition: [dict] = None):
    str_list = _str.split('.', 1)
    for rel in str_list:
        if rel == str_list[-1]:
            return _dict[rel]
        if rel.isdigit():
            if not condition:
                return get_path_dict_condition(str_list[1], _dict[int(rel)], condition)
            keys = list(condition[0].keys())
            for dic in _dict:
                if condition[0][keys[0]] == dic[keys[0]]:
                    del condition[0]
                    return get_path_dict_condition(str_list[1], dic, condition)
            return None
        if rel in _dict.keys():
            return get_path_dict_condition(str_list[1], _dict[rel], condition)
        return None


# 针对性函数，将字符串类型的condition，转换成list[dict]  例如'{"a":1}, {"b":"user"}' --> [{"a":1}， {"b":"user"}]
def get_condition(condition):
    condition_list = []
    if not condition: return None
    condition_split = condition.split(",")
    for cond in condition_split:
        condition_list.append(
            json.loads(cond)
        )
    return condition_list


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


# 基本计算器
class cal:
    @staticmethod
    def add(x, y):
        return x + y

    @staticmethod
    def subtract(x, y):
        return x - y

    @staticmethod
    def multiply(x, y):
        return x * y

    @staticmethod
    def divide(x, y):
        return x / y


def make_class_list(data_list, className, filterList, parents=None):
    class_list = []
    for asserts in data_list:
        class_list.append(
            make_class(asserts, className, filterList, parents)
        )
    return class_list


def make_class(data,className, filterList, parents=None):
    if parents:
        data.update(parents)
    inAsserts = {}
    for filters in filterList:
        inAsserts.update({
            filters: data[filters]
        })
    return className(inAsserts)
