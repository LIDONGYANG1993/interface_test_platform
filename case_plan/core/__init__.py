#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇


def get_path_dict(_str: str, _dict: dict):
    str_list = _str.split('.', 1)
    for rel in str_list:
        if rel == str_list[-1]:
            return _str, _dict[rel]
        if rel.isdigit():
            return get_path_dict(str_list[1], _dict[int(rel)])
        if rel in _dict.keys():
            return get_path_dict(str_list[1], _dict[rel])
        return _str, None
