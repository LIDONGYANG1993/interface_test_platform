#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json
import threading
from copy import deepcopy
from typing import List, Set, Any

import requests
from requests import Response

from config.casePlan.yamlFilersZh import *
from case_plan.core.func import *

asserts_used = []


class publicDone:
    def __init__(self, data: dict):
        self.data = data
        self.keys = data.keys()
        self.thread = []

    def _get_value(self, key) -> None or str:
        if key in self.keys:
            return self.data[key]
        return None

    def _thread_add(self, func, params=None):
        if params is None: params = []
        thread = threading.Thread(target=func, args=params)
        self.thread.append(thread)

    @staticmethod
    def _thread_run_join(func, params=None):
        if params is None: params = []
        thread = threading.Thread(target=func, args=params)
        thread.start(), thread.join()

    @staticmethod
    def public_variable(step=None, case=None, plan=None):
        step: stepDone
        case: caseDone
        plan: planDone
        res = {}
        if plan:
            res.update(plan.variable_dict())
        if case:
            res.update(case.variable_dict())
        if step:
            res.update(step.extractor_result)
            res.update(step.calculator_result)
        return res

    def variable_replace(self, data, replaceData: dict):
        if isinstance(data, str):
            return self.str_replace(data, replaceData)
        if isinstance(data, dict):
            return self.dict_replace(data, replaceData)

    @staticmethod
    def str_replace(data, replaceData):
        data_copy = deepcopy(data)
        data_copy = data_copy.replace("{{","{").replace("}}","}")
        try:
            res = data_copy.format(**replaceData)
        except Exception as e:
            return data
        return res

    def dict_replace(self, data: dict, replaceData):
        for data_key in data.keys():
            data[data_key] = self.str_replace(data[data_key], replaceData)
        return data

class extractorDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.filedPath = self.get_filedPath
        self.step = self.get_step
        self.condition = self.get_condition
        self.name = self.get_name

        self.value = None

    @property
    def get_name(self):
        return self._get_value(extractorFiler.name)

    @property
    def get_filedPath(self):
        return self._get_value(extractorFiler.value)

    @property
    def get_condition(self):
        return self._get_value(extractorFiler.condition)

    @property
    def get_step(self):
        return self._get_value(extractorFiler.step)

    def get_value(self, data: dict):
        self.value = get_path_dict_condition(self.filedPath, data, self.condition)

class calculaterDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.result = None
        self.name = self.get_name
        self.step = self.get_name
        self.variable1 = self.get_variable1
        self.variable2 = self.get_variable2
        self.calFunction = self.get_calFunction


    @property
    def get_name(self):
        return self._get_value(calculatorFiler.name)

    @property
    def get_step(self):
        return self._get_value(calculatorFiler.step)

    @property
    def get_variable1(self):
        return self._get_value(calculatorFiler.Variable1)

    @property
    def get_calFunction(self):
        return self._get_value(calculatorFiler.calFunction)

    @property
    def get_variable2(self):
        return self._get_value(calculatorFiler.Variable2)

    def calculate(self):
        if self.calFunction == "add":
            return cal.add(self.variable1, self.variable2)
        if self.calFunction == "subtract":
            return cal.subtract(self.variable1, self.variable2)
        if self.calFunction == "multiply":
            return cal.multiply(self.variable1, self.variable2)
        if self.calFunction == "divide":
            return cal.divide(self.variable1, self.variable2)
        return None

    def get_result(self):
        self.replace_in_calculater()
        self.result = self.calculate()


    def replace_in_calculater(self):
        self.step: stepDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case, self.step.case.plan)
        if not variable: return
        self.variable1 = self.variable_replace(self.variable1, variable)
        self.variable2 = self.variable_replace(self.variable2, variable)


class assertsDone(publicDone):
    def __init__(self, data: dict):
        super().__init__(data)
        self.result = None
        self.value1 = self.get_value1

        self.case = self.get_case
        self.value2 = self.get_value2
        self.assertMethod = self.get_assertMethod
        self.step = self.get_step

        self.asserts_str = self.get_asserts_str




    def replace_in_asserts(self):
        self.step: stepDone
        self.case: caseDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case, self.step.case.plan)
        elif self.case:
            variable = self.public_variable(None, self.case, self.case.plan)
        if not variable: return
        self.asserts_str = self.variable_replace(self.asserts_str, variable)


    @property
    def get_value1(self):
        return self._get_value(assertsFiler.value1)

    @property
    def get_step(self):
        return self._get_value(assertsFiler.step)

    @property
    def get_case(self):
        return self._get_value(assertsFiler.case)

    @property
    def get_assertMethod(self):
        return self._get_value(assertsFiler.assertMethod)

    @property
    def get_value2(self):
        return self._get_value(assertsFiler.value2)

    @property
    def get_asserts_str(self):
        if not self.value1 or not self.value2 or not self.assertMethod:
            return None
        return str(self.value1) + str(self.assertMethod) + str(self.value2)

    def asserts(self):
        if not self.asserts_str:
            return None
        self.replace_in_asserts()
        res = eval(self.asserts_str)
        return res

    def get_result(self):
        self.result = {
            assertsFiler.step: self.step,
            assertsFiler.case: self.case,
            assertsFiler.value1: self.value1,
            assertsFiler.assertMethod: self.assertMethod,
            assertsFiler.value2: self.value2,
            assertsFiler.result: self.asserts()
        }


class requestDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.host = self.get_host
        self.path = self.get_path

        self.headers = self.get_headers

        self.params = self.get_params
        self.post_data = self.get_data
        self.method = self.get_method
        self.step = self.get_step
        self.response = None
        self.error = False
        self.code = 0

    def replace_in_requestInfo(self):
        self.step: stepDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case, self.step.case.plan)
        if not variable: return
        self.host = self.variable_replace(self.host, variable)
        self.path = self.variable_replace(self.path, variable)
        self.params = self.variable_replace(self.params, variable)
        self.data = self.variable_replace(self.data, variable)
        self.post_data = self.variable_replace(self.post_data, variable)


    @property
    def get_name(self):
        return self._get_value(requestInfoFiler.name)

    @property
    def get_params(self):
        return self._get_value(requestInfoFiler.params)

    @property
    def get_data(self):
        return self._get_value(requestInfoFiler.data)

    @property
    def get_host(self):
        return self._get_value(requestInfoFiler.host)

    @property
    def get_path(self):
        return self._get_value(requestInfoFiler.path)

    @property
    def get_headers(self):
        return self._get_value(requestInfoFiler.headers)

    @property
    def get_method(self):
        return self._get_value(requestInfoFiler.method)

    @property
    def get_step(self):
        return self._get_value(requestInfoFiler.step)

    def request(self):
        self.replace_in_requestInfo()
        if self.method == "GET":
            self.response = requests.get(url=self.host + self.path, params=self.params, headers=self.headers)
        else:
            self.response = requests.get(url=self.host + self.path, params=self.params, data=self.post_data,
                                         headers=self.headers)

    def asserts(self):
        self.response: requests.Response
        if self.response.status_code == 200:
            self.error = True
            self.code = self.response.status_code


class variableDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.value = self.get_value
        self.case = self.get_case
        self.plan = self.get_plan

    @property
    def get_name(self):
        return self._get_value(variableFiler.name)

    @property
    def get_value(self):
        return self._get_value(variableFiler.value)

    @property
    def get_case(self):
        return self._get_value(variableFiler.case)

    @property
    def get_plan(self):
        return self._get_value(variableFiler.plan)


class stepDone(publicDone):
    response: Response
    calculator_list: [calculaterDone]

    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.case = self.get_case
        self.stepNumber = self.get_stepNumber
        self.reParams = self.get_reParams
        self.requestInfo: requestDone = self.get_requestInfo
        self.asserts_list: [assertsDone] = self.get_asserts_list
        self.extractor_list: [extractorDone] = self.get_extractor_list
        self.calculator_list = self.get_calculator_list
        self.extractor_result = {}
        self.calculator_result = {}
        self.asserts_result = []
        self.error = False
        self.log = []
        self.code = 0

    @property
    def get_name(self):
        return self._get_value(stepFiler.name)

    @property
    def get_case(self):
        return self._get_value(stepFiler.case)

    @property
    def get_stepNumber(self):
        return self._get_value(stepFiler.stepNumber)

    @property
    def get_reParams(self):
        return self._get_value(stepFiler.reParams)

    @property
    def get_plan(self):
        return self._get_value(variableFiler.plan)

    @property
    def get_requestInfo(self):
        parents = {requestInfoFiler.step:self}
        return make_class(self._get_value(stepFiler.requestInfo), requestDone, requestInfoFiler.used, parents)

    @property
    def get_asserts_list(self):
        parents = {assertsFiler.step:self,assertsFiler.case:None}
        return make_class_list(self._get_value(stepFiler.assertList), assertsDone, assertsFiler.used, parents)

    @property
    def get_extractor_list(self):
        parents = {extractorFiler.step:self}
        return make_class_list(self._get_value(stepFiler.extractor), extractorDone, extractorFiler.used, parents)

    @property
    def get_calculator_list(self):
        parents = {calculatorFiler.step:self}
        return make_class_list(self._get_value(stepFiler.calculator), calculaterDone, calculatorFiler.used, parents)


    def replace_in_requestInfo(self):
        self.case: caseDone
        variable = None
        if self.case:
            variable = self.public_variable(None, self.case, self.case.plan)
        if not variable: return
        self.reParams = self.variable_replace(self.reParams, variable)



    def request(self):
        self.replace_in_requestInfo()
        if self.reParams:
            self.requestInfo.params.update(self.reParams)
        self._thread_run_join(self.requestInfo.request)

    def asserts_response(self):
        self.requestInfo.asserts()
        self.response = self.requestInfo.response
        self.error = self.requestInfo.error
        self.code = -10001


    def extractor_in_step(self):
        for extractor in self.extractor_list:
            extractor: extractorDone
            extractor.get_value(self.response.json())
            self.extractor_result.update({extractorFiler.name: extractor.value})

    def calculater_in_step(self):
        for calculater in self.calculator_list:
            calculater: calculaterDone
            calculater.get_result()
            self.calculator_result.update({calculatorFiler.name: calculater.result})

    def asserts_in_step(self):
        for asserts in self.asserts_list:
            asserts: assertsDone
            asserts.get_result()
            self.asserts_result.append(asserts.result)

    def run_in_step(self):
        self.request()
        self.asserts_response()
        if self.error: return
        self.extractor_in_step()
        self.calculater_in_step()
        self.asserts_in_step()
        return self


class caseDone(publicDone):

    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.plan = self.get_plan
        self.variable = self.get_variable
        self.caseNumber = self.get_caseNumber

        self.asserts_result = []


        self.step_list = self.get_step_list
        self.asserts_list = self.get_asserts_list

        self.extractor_result = {}
        self.calculater_result = {}
        self.replace_result = {}


    @property
    def get_name(self):
        return self._get_value(caseFiler.name)

    @property
    def get_caseNumber(self):
        return self._get_value(caseFiler.caseNumber)

    @property
    def get_plan(self):
        return self._get_value(caseFiler.plan)


    @property
    def get_variable(self):
        parents = {variableFiler.case:self,variableFiler.plan:None}
        return make_class_list(self._get_value(caseFiler.variable), variableDone, variableFiler.used, parents)

    @property
    def get_step_list(self):
        parents = {stepFiler.case:self}
        return make_class_list(self._get_value(caseFiler.stepList), stepDone, stepFiler.used, parents)

    @property
    def get_asserts_list(self):
        parents = {assertsFiler.case:self,assertsFiler.step:None}
        return make_class_list(self._get_value(caseFiler.assertList), assertsDone, assertsFiler.used,parents)



    def variable_dict(self):
        res = {}
        for variable in self.variable:
            variable: variableDone
            res.update(
                {
                    variable.name: variable.value
                }
            )
        return res

    def asserts_in_case(self):
        for asserts in self.asserts_list:
            asserts: assertsDone
            asserts.get_result()
            self.asserts_result.append(asserts.result)

    def update_variable(self):
        self.variable.update(self.plan.variable)

    def run_in_case(self):
        for step in self.step_list:
            step: stepDone
            self._thread_run_join(step.run_in_step)
            self.extractor_result.update(step.extractor_result)
            self.calculater_result.update(step.calculator_list)
            self.asserts_in_case()

    def get_replace_result(self):
        if self.plan:
            self.plan: planDone
            self.replace_result.update(self.plan.replace_result)
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)
        self.replace_result.update(self.calculater_result)


class planDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.variable = self.get_variable
        self.extractor_result = {}
        self.calculater_result = {}
        self.replace_result = {}
        self.case_list = self.get_case_list



    @property
    def get_variable(self):
        parents = {variableFiler.plan:self,variableFiler.case:None}
        return make_class_list(self._get_value(planFiler.globalVariable), variableDone, variableFiler.used, parents)

    @property
    def get_name(self):
        return self._get_value(planFiler.name)


    @property
    def get_case_list(self):
        parents = {caseFiler.plan:self}
        return make_class_list(self._get_value(planFiler.caseList), caseDone, caseFiler.used, parents)

    def run_in_plan(self):
        for case in self.case_list:
            case: caseDone
            self._thread_run_join(case.run_in_case)
            self.extractor_result.update(case.extractor_result)

    def get_replace_result(self):
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)

    def variable_dict(self):
        res = {}
        for variable in self.variable:
            variable: variableDone
            res.update(
                {
                    variable.name: variable.value
                }
            )
        return res


def responseDoneTest():
    res = extractorDone({extractorFiler.value: "a.b.0.e.0.z", "condition": '{"c":10},{"w": "12"}'})
    res.get_value({
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

    print(res.value)


def calculaterDoneTest():
    cals = calculaterDone(
        {
            calculatorFiler.Variable1: 10,
            calculatorFiler.Variable2: 3,
            calculatorFiler.calFunction: "divide"
        }
    )
    cals.get_result()
    print(cals.result)


def assertsDoneTest():
    from case_plan.core.data import assertData
    asserts = assertsDone(assertData(1).data_dict)
    asserts.get_result()
    print(asserts.asserts_str)


def planDoneTest():
    from case_plan.core.data import planData

    from case_plan.core import planTest
    plan = planDone(planTest)
    plan.run_in_plan()
    print("END")


if __name__ == '__main__':
    planDoneTest()
