#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json
from typing import List, Set, Any

import requests
from case_plan.core import get_path_dict_condition

from config.casePlan.filers import *


class publicDone:
    def __init__(self, data: dict):
        self.kwargs = data
        self.keys = data.keys()

    def _get_value(self, key) -> None or str:
        if key in self.keys:
            return self.kwargs[key]
        return None

class responseDone(publicDone):
    def __init__(self, data):
        super().__init__(data)

    @property
    def name(self):
        return self._get_value(responseFiler.name)

    @property
    def filedPath(self):
        return self._get_value(responseFiler.fieldPath)

    @property
    def condition(self):
        return self._get_value(responseFiler.condition)

    @property
    def step(self):
        return self._get_value(responseFiler.step)

    def get_value(self, data: dict):
        return get_path_dict_condition(self.filedPath, data, self.condition)



class requestDone(publicDone):
    def __init__(self, data):
        super().__init__(data)

    @property
    def name(self):
        return self._get_value(stepFiler.interfaceName)

    @property
    def params(self):
        return self._get_value(stepFiler.params)

    @property
    def data(self):
        return self._get_value(stepFiler.data)

    @property
    def host(self):
        return self._get_value(stepFiler.host)

    @property
    def path(self):
        return self._get_value(stepFiler.path)

    @property
    def headers(self):
        return self._get_value(stepFiler.headers)

    @property
    def method(self):
        return self._get_value(stepFiler.method)

    def request(self):
        if self.method == "GET":
            return requests.get(url=self.host + self.path, params=self.params, headers=self.headers)
        else:
            return requests.get(url=self.host + self.path, params=self.params, data=self.data, headers=self.headers)

    def log(self):
        pass





def responseDoneTest():
    res = responseDone({responseFiler.fieldPath: "a.b.0.e.0.z", "condition": '{"c":10},{"w": "12"}'}).get_value({
        "a": {
            "b": [
                {"d": 1, "c": 10, "e": [
                    {
                        "z": "5",
                        "w": "7",
                    },
                    {
                        "z": "9",
                        "w": "12",
                    }
                ]

                 },
                {"d": "aaa", "c": 5}
            ]
        }
    }, )

    print(res)



if __name__ == '__main__':
    responseDoneTest()
