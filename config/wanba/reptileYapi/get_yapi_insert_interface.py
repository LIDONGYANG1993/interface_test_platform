#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2021/8/22
# @Name  : 杨望宇
from config.wanba.reptileYapi import *
from config.wanba.reptileYapi.common.yapiInformation import yapiInformation
from case_plan.models import requestInfoModel


class Interface:
    def __init__(self):
        self.yapi = yapiInformation(yapi_name,yapi_pwd)
        self.projects = []
        self.cats = []
        self.interfaces = []


    def get_cat_interface(self, cat_id):
        return self.yapi.get_interfaces_for_cat(cat_id)

    @staticmethod
    def get_from_database(path):
        try:
            info = requestInfoModel.objects.get(path=path)
        except Exception:
            return None
        return info

    @staticmethod
    def create_new(params):
        info = requestInfoModel.objects.create(**params)
        info.save()

    def get_dict(self, yapi_interface:dict):
        return dict(
            path=self.make_path(yapi_interface),
            method=self.make_method(yapi_interface),
            name=self.make_name(yapi_interface),
            params=self.make_params(yapi_interface),
            doc_url=self.make_doc_url(yapi_interface)
        )

    @staticmethod
    def make_path(yapi_interface:dict):
        return yapi_interface.get("path", None)

    @staticmethod
    def make_method(yapi_interface:dict):
        return yapi_interface.get("method", None)


    @staticmethod
    def make_doc_url(yapi_interface:dict):
        return yapi_interface.get("documentUrl", None)

    @staticmethod
    def make_name(yapi_interface:dict):
        return yapi_interface.get("name", None)

    @staticmethod
    def make_params(yapi_interface:dict):
        res = {}
        body = yapi_interface.get("body", None)
        properties = body.get("properties", None)
        if not properties:
            return res
        for key in properties.keys():
            res.update({key: properties[key].get("type")})
        return res

    def import_data_by_cat(self, cat_id):
        success = []
        fail = []
        exited = []
        try:
            face = self.get_cat_interface(cat_id)
        except Exception as e:
            return False,  {"success": success, "fail": fail, "exited": exited}
        for face_rel in face:
            try:
                if self.get_from_database(face_rel.get("path")):
                    exited.append(self.get_dict(face_rel))
                    continue
                self.create_new(self.get_dict(face_rel))
            except Exception as e:
                fail.append(self.get_dict(face_rel))
                continue
            success.append(self.get_dict(face_rel))
        return True, {"success": success, "fail": fail, "exited": exited}


if __name__ == '__main__':
    run = Interface()
    pass
