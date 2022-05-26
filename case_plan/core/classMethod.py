#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import requests
from case_plan.core import get_path_dict

from config.casePlan.filers import *


class publicDone:
    def __init__(self, data:dict):
        self.kwargs = data
        self.keys = data.keys()

    def _get_value(self, key):
        if key in self.keys:
            return self.kwargs[key]
        return None


class responseDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name()
        self.filedPath = self.get_filedPath()
        self.condition = self.get_condition()
        self.step = self.get_step()

    def get_name(self):
        key = responseFiler.name
        return self._get_value(key)

    def get_filedPath(self):
        key = responseFiler.fieldPath
        return self._get_value(key)

    def get_condition(self):
        key = responseFiler.condition
        return self._get_value(key)

    def get_step(self):
        key = responseFiler.step
        return self._get_value(key)

    def get_value(self, data: dict, condition=None):
        return get_path_dict(self.filedPath, data)


class requestDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name()
        self.host = self.get_host()
        self.path = self.get_path()
        self.method = self.get_method()
        self.params = self.get_params()
        self.data = self.get_data()
        self.headers = self.get_headers()

    def get_name(self):
        key = stepFiler.interfaceName
        return self._get_value(key)

    def get_params(self):
        key = stepFiler.params
        return self._get_value(key)

    def get_data(self):
        key = stepFiler.data
        return self._get_value(key)

    def get_host(self):
        key = stepFiler.host
        return self._get_value(key)

    def get_path(self):
        key = stepFiler.path
        return self._get_value(key)

    def get_headers(self):
        key = stepFiler.path
        return self._get_value(key)

    def get_method(self):
        key = stepFiler.method
        return self._get_value(key)

    def request(self):
        if self.method == "GET":
            return requests.get(url=self.host + self.path, params=self.params, headers=self.headers)
        else:
            return requests.get(url=self.host + self.path, params=self.params, data=self.data, headers=self.headers)

    def log(self):
        pass


def responseDoneTest():
    res = responseDone({responseFiler.fieldPath: "a.b.0.d"}).get_value({
        "a": {
            "b": [
                {"d": 1},
                {"d": 2}
            ]
        }
    })

    print(res)


if __name__ == '__main__':
    responseDoneTest()