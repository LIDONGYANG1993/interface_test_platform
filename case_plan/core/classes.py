#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json
import os.path
import threading
import time
from copy import deepcopy
from config.wanba.interfaceRequest import get_token, app_request
from config.casePlan import defaultParams
import requests
from requests import Response
from config.casePlan.yamlFilersZh import *
from case_plan.core.func import *

from config.logger import Logger, project_path

asserts_used = []
log_path = os.path.join(project_path, "logs", "class", "logs_{}.log".format(int(time.time())))

the_logger = Logger(log_path, 'debug', 10, "%(asctime)s-%(message)s").logger


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
        thread.start()
        thread.join()

    @staticmethod
    def _run(func, params=None):
        if not params:
            return func()
        return func(params)

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
            res.update(case.extractor_result)
            res.update(case.calculater_result)
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
        data_copy = data_copy.replace("{{", "{").replace("}}", "}")
        try:
            res = data_copy.format(**replaceData)
        except Exception as e:
            return data
        return res

    def dict_replace(self, data: dict, replaceData):
        for data_key in data.keys():
            data[data_key] = self.variable_replace(data[data_key], replaceData)
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
        condition_list = []
        condition = self.condition
        if self.condition == "":
            condition = None
        if condition:
            for con in condition.split(","):
                condition_list.append(json.loads(con))
        try:
            self.value = get_path_dict_condition(self.filedPath, data, condition_list)
        except Exception:
            self.value = None
            the_logger.debug("提取结果失败：value-{}, response--{}".format(self.filedPath, data))


class calculaterDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.result = None
        self.name = self.get_name
        self.step = self.get_step
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

        variable1 = float(self.variable1)
        variable2 = float(self.variable2)
        if self.calFunction == "add":
            return cal.add(variable1, variable2)
        if self.calFunction == "subtract":
            return cal.subtract(variable1, variable2)
        if self.calFunction == "multiply":
            return cal.multiply(variable1, variable2)
        if self.calFunction == "divide":
            return cal.divide(variable1, variable2)
        return None

    def get_result(self):
        self.replace_in_calculater()
        self.result = None
        if is_number(self.variable1) and is_number(self.variable2):
            self.result = self.calculate()

    def replace_in_calculater(self):
        self.step: stepDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case if self.step.case else None,
                                            self.step.case.plan if self.step.case and self.step.case.plan else None)
        if not variable: return
        self.variable1 = self.variable_replace(self.variable1, variable)
        self.variable2 = self.variable_replace(self.variable2, variable)

    def calculater_for_api(self):
        return {
            calculatorFiler.name: self.name,
            calculatorFiler.Variable1: self.variable1,
            calculatorFiler.calFunction: self.calFunction,
            calculatorFiler.Variable2: self.variable2,
            calculatorFiler.result: self.result,
        }


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
        self.asserts_result = None
        self.fail = None
        self.asserts_result_dict = {}

    def replace_in_asserts(self):
        self.step: stepDone
        self.case: caseDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case if self.step.case else None,
                                            self.step.case.plan if self.step.case and self.step.case.plan else None)
        elif self.case:
            variable = self.public_variable(None, self.case, self.case.plan if self.case.plan else None)
        if not variable: return
        self.value1 = self.variable_replace(self.value1, variable)
        self.value2 = self.variable_replace(self.value2, variable)

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
        if is_number(self.value1) and is_number(self.value2):
            return str(self.value1) + str(self.assertMethod) + str(self.value2)
        return '"{}"'.format(str(self.value1)) + str(self.assertMethod) + '"{}"'.format(str(self.value2))

    def asserts(self):
        self.replace_in_asserts()
        self.asserts_str = self.get_asserts_str
        if not self.asserts_str:
            return None
        self.asserts_result = eval(self.asserts_str)
        self.fail = not self.asserts_result
        return self.asserts_result

    def get_result(self):

        self.result = {
            assertsFiler.step: self.step,
            assertsFiler.case: self.case,
            assertsFiler.value1: self.value1,
            assertsFiler.assertMethod: self.assertMethod,
            assertsFiler.value2: self.value2,
        }
        try:
            self.result.update({assertsFiler.result: self.asserts()})
        except Exception:
            self.result.update({assertsFiler.result: False})

    def asserts_result_for_api(self):
        return {
            assertsFiler.value1: self.value1,
            assertsFiler.assertMethod: self.assertMethod,
            assertsFiler.value2: self.value2,
            assertsFiler.assertStr: self.asserts_str,
            assertsFiler.result: self.asserts_result
        }


class requestDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.msg = None
        self.name = self.get_name
        self.host = self.get_host
        self.path = self.get_path

        self.headers = self.get_headers

        self.params = self.get_params
        self.post_data = self.get_data
        self.method = self.get_method
        self.step = self.get_step

        self.environment = self.get_environment()

        self.response = None
        self.response_json = None
        self.error = None
        self.code = 0

    def replace_in_requestInfo(self):
        self.step: stepDone
        variable = None
        if self.step:
            variable = self.public_variable(self.step, self.step.case if self.step.case else None,
                                            self.step.case.plan if self.step.case and self.step.case.plan else None)
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
        the_logger.debug("START-REQUEST,  {}, {}, {}, {}".format(self.name, self.host if self.host else None, self.path,
                                                                 self.params), )
        self.replace_in_requestInfo()
        if self.host:
            self.request_for_public()
        else:
            self.request_for_wanba()
        the_logger.debug("END-REQUEST,  {}, {}, {}, {}".format(self.name, self.host if self.host else None, self.path,
                                                               self.response.json() if self.error is False else None))

    def request_for_wanba(self):
        self.response = app_request(case_url=self.path, params=self.params, environment=self.environment)

    def request_for_public(self):
        if self.method == "GET":
            self.response = requests.get(url=self.host + self.path, params=self.params, headers=self.headers)

        else:
            self.response = requests.get(url=self.host + self.path, data=self.params, headers=self.headers)

    def asserts(self):
        self.response: requests.Response

        if not self.response:
            self.error = True
            self.code = 99999
            self.response_json = None

        elif self.response.status_code != 200:
            self.error = True
            self.code = self.response.status_code
            self.response_json = None
        else:
            self.error = False
            self.code = self.response.status_code
            self.response_json = self.response.json()

    def assert_wanba(self):
        if self.error is True: return
        if self.response.json()["code"] == 10202 or self.response.json()["code"] == 3:
            get_token(self.params, self.environment)
            self.request()
            self.asserts()

    def result_for_api(self):
        self.result_massage()
        return {
            requestInfoFiler.name: self.name,
            requestInfoFiler.host: self.host,
            requestInfoFiler.path: self.path,
            requestInfoFiler.params: self.params,
            requestInfoFiler.result: self.response_json,
            "msg": self.msg

        }

    def result_massage(self):
        msg = []
        if self.error is None or self.error is True:
            msg.append("接口：{},访问失败！\n".format(self.name))
        else:
            msg.append("接口：{},访问成功！\n".format(self.name))
        self.msg = msg

    def make_environment(self):
        environment = self.get_environment()

    def get_environment(self):
        if not self.step: return defaultParams
        if not self.step.case: return defaultParams
        if not self.step.case.plan: return defaultParams
        return self.step.case.plan.environment


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
        self.msg = None
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
        self.asserts_result_for_api = []
        self.calculator_result_for_api = []
        self.asserts_result = []
        self.error = None
        self.fail = None
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
        parents = {requestInfoFiler.step: self}
        return make_class(self._get_value(stepFiler.requestInfo), requestDone, requestInfoFiler.used, parents)

    @property
    def get_asserts_list(self):
        parents = {assertsFiler.step: self, assertsFiler.case: None}
        return make_class_list(self._get_value(stepFiler.assertList), assertsDone, assertsFiler.used, parents)

    @property
    def get_extractor_list(self):
        parents = {extractorFiler.step: self}
        return make_class_list(self._get_value(stepFiler.extractor), extractorDone, extractorFiler.used, parents)

    @property
    def get_calculator_list(self):
        parents = {calculatorFiler.step: self}
        return make_class_list(self._get_value(stepFiler.calculator), calculaterDone, calculatorFiler.used, parents)

    def replace_in_step(self):
        self.case: caseDone
        variable = None
        if self.case:
            variable = self.public_variable(None, self.case, self.case.plan if self.case.plan else None)
        if not variable: return
        self.reParams = self.variable_replace(self.reParams, variable)

    def request(self):
        self.replace_in_step()
        if self.reParams:
            self.requestInfo.params.update(self.reParams)
        self._thread_run_join(self.requestInfo.request)

    def asserts_response(self):
        self.requestInfo.asserts()
        self.requestInfo.assert_wanba()
        self.response = self.requestInfo.response
        self.error = self.requestInfo.error
        self.code = self.requestInfo.code

    def extractor_in_step(self):
        for extractor in self.extractor_list:
            extractor: extractorDone
            the_logger.debug("START-EXTRACTOR: {} ".format(extractor.name))
            self._thread_run_join(func=extractor.get_value, params=[self.response.json()])
            the_logger.debug("END-EXTRACTOR: {}--{} ".format(extractor.name, extractor.value))
            self.extractor_result.update({extractor.name: extractor.value})

    def calculater_in_step(self):
        for calculater in self.calculator_list:
            calculater: calculaterDone
            the_logger.debug(
                "START-EXTRACTOR: {} {} {}".format(calculater.variable1, calculater.calFunction, calculater.variable2))
            self._thread_run_join(func=calculater.get_result)
            the_logger.debug("START-EXTRACTOR: {} {} {} == {}".format(calculater.variable1, calculater.calFunction,
                                                                      calculater.variable2, calculater.result))
            self.calculator_result.update({calculater.name: calculater.result})
            self.calculator_result_for_api.append(calculater.calculater_for_api())

    def asserts_in_step(self):
        for asserts in self.asserts_list:
            if self.fail: return
            asserts: assertsDone
            the_logger.debug("START-ASSERT-CASE: {} ".format(asserts.asserts_str))
            self._thread_run_join(func=asserts.get_result)
            the_logger.debug("END-ASSERT-CASE: {}--{}".format(asserts.asserts_str, asserts.asserts_result))
            if not asserts.asserts_result:
                self.fail = True
            else: self.fail = False
            self.asserts_result.append({assertsFiler.assertStr: asserts.asserts_str, assertsFiler.result: asserts.result})
            self.asserts_result_for_api.append(asserts.asserts_result_for_api())
        return

    def run_in_step(self):
        self.request()
        self.asserts_response()
        if self.error:
            self.fail = True
            return
        self.extractor_in_step()
        self.calculater_in_step()
        self.asserts_in_step()

    def result_for_api(self):
        self.result_massage()
        return {
            stepFiler.name: self.name,
            stepFiler.stepNumber: self.stepNumber,
            stepFiler.requestInfo: self.requestInfo.result_for_api(),
            stepFiler.extractor: self.extractor_result,
            stepFiler.calculator: self.calculator_result_for_api,
            stepFiler.assertList: self.asserts_result_for_api,
            "msg": self.msg

        }

    def result_massage(self):
        msg = []
        if self.error:
            msg.append("步骤：{},执行异常！\n".format(self.name))
        elif self.fail is None or self.fail is True:
            msg.append("步骤：{},执行失败！\n".format(self.name))
        else:
            msg.append("步骤：{},执行成功！\n".format(self.name))
        for asserts in self.asserts_list:
            if not asserts.asserts_result:
                msg.append("验证：{},验证失败！\n".format(asserts.asserts_str))
                break
            else:
                msg.append( "验证：{}, 验证成功！\n".format(asserts.asserts_str))
        self.msg = msg



class caseDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.msg = None
        self.name = self.get_name
        self.plan = self.get_plan
        self.variable = self.get_variable
        self.caseNumber = self.get_caseNumber

        self.asserts_result = []

        self.step_list = self.get_step_list
        self.asserts_list = self.get_asserts_list

        self.fail = None
        self.asserts_result_for_api = []

        self.step_result_for_api = []
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
        parents = {variableFiler.case: self, variableFiler.plan: None}
        return make_class_list(self._get_value(caseFiler.variable), variableDone, variableFiler.used, parents)

    @property
    def get_step_list(self):
        parents = {stepFiler.case: self}
        return make_class_list(self._get_value(caseFiler.stepList), stepDone, stepFiler.used, parents)

    @property
    def get_asserts_list(self):
        parents = {assertsFiler.case: self, assertsFiler.step: None}
        return make_class_list(self._get_value(caseFiler.assertList), assertsDone, assertsFiler.used, parents)

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
        if self.fail:
            return
        for asserts in self.asserts_list:
            if self.fail: return
            asserts: assertsDone
            the_logger.debug("START-ASSERT-CASE: {} ".format(asserts.asserts_str))
            self._thread_run_join(asserts.get_result)
            the_logger.debug("END-ASSERT-CASE: {}--{}".format(asserts.asserts_str, asserts.asserts_result))
            self.asserts_result.append(
                {assertsFiler.assertStr: asserts.asserts_str, assertsFiler.result: asserts.result})
            self.asserts_result_for_api.append(asserts.asserts_result_for_api())
            if not asserts.asserts_result:
                self.fail = True

    def update_variable(self):
        self.variable.update(self.plan.variable)

    def run_in_case(self):
        for step in self.step_list:
            step: stepDone
            if self.fail: return
            the_logger.debug("START-STEP, {}-{} ".format(step.stepNumber, step.name))
            self._thread_run_join(step.run_in_step), time.sleep(0)
            the_logger.debug("END-STEP, {}-{} ".format(step.stepNumber, step.name))
            self.extractor_result.update(step.extractor_result)
            self.calculater_result.update(step.calculator_result)
            self.step_result_for_api.append(step.result_for_api())
            if not (step.error is False) or not (step.fail is False): self.fail = True
            else:self.fail = False
        self.asserts_in_case()

    def get_replace_result(self):
        if self.plan:
            self.plan: planDone
            self.replace_result.update(self.plan.replace_result)
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)
        self.replace_result.update(self.calculater_result)

    def result_for_api(self):
        self.result_massage()
        return {
            caseFiler.name: self.name,
            caseFiler.stepList: self.step_result_for_api,
            caseFiler.assertList: self.asserts_result_for_api,
            "msg": self.msg
        }

    def result_massage(self):
        msg = []
        for step in self.step_list:
            step: stepDone
            if not (step.error is False):
                msg.append( "步骤：{}-{},执行异常！\n".format(step.stepNumber, step.name))
                break
            elif not (step.fail is False):
                msg.append("步骤：{}-{},执行失败！\n".format(step.stepNumber, step.name))
                break
            else:
                msg.append("步骤：{}-{},执行成功！\n".format(step.stepNumber, step.name))
        for asserts in self.asserts_list:
            if not (asserts.fail is False):
                msg.append("验证：{},验证失败！\n".format(asserts.asserts_str))
                break
            else:
                msg.append("验证：{}, 验证成功！\n".format(asserts.asserts_str))
        self.msg = msg

class planDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.variable = self.get_variable
        self.environment = self.get_environment
        self.extractor_result = {}
        self.calculater_result = {}
        self.replace_result = {}
        self.case_result_for_api = []
        self.case_list = self.get_case_list

        self.msg = None


    @property
    def get_variable(self):
        parents = {variableFiler.plan: self, variableFiler.case: None}
        return make_class_list(self._get_value(planFiler.globalVariable), variableDone, variableFiler.used, parents)

    @property
    def get_name(self):
        return self._get_value(planFiler.name)

    @property
    def get_environment(self):
        return self._get_value(planFiler.environment)

    @property
    def get_case_list(self):
        parents = {caseFiler.plan: self}
        return make_class_list(self._get_value(planFiler.caseList), caseDone, caseFiler.used, parents)

    def run_in_plan(self):
        the_logger.debug("START-PLAN")

        for case in self.case_list:
            case: caseDone

            the_logger.debug("START-CASE: {} ".format(case.name))
            self._thread_run_join(case.run_in_case)
            the_logger.debug("END-CASE: {} ".format(case.name, not case.fail))
            self.extractor_result.update(case.extractor_result)
            self.case_result_for_api.append(case.result_for_api())
        the_logger.debug("END-PLAN")

    def get_replace_result(self):
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)

    def result_for_api(self):
        self.result_massage()
        return {
            planFiler.name: self.name,
            planFiler.environment: self.environment,
            planFiler.caseList: self.case_result_for_api,
            "msg":self.msg

        }

    def result_massage(self):
        msg = []
        for case in self.case_list:
            case: caseDone
            if not (case.fail is False):
                msg.append("用例：{},执行失败！\n".format(case.name))
            else:
                msg.append("用例：{},执行成功！\n".format(case.name))
        self.msg = msg

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


def assertsDoneTest():
    from case_plan.core.data import assertData
    asserts = assertsDone(assertData(1).data_dict)
    asserts.get_result()
    print(asserts.asserts_str)


def planDoneTest():
    from case_plan.core.data import planData

    from case_plan.core import planTest
    plan = planDone(planData(dataId=1).data_dict)
    plan.run_in_plan()
    print("END")


def requestDoneTest():
    from case_plan.core import requestInfo
    req = requestDone(requestInfo)
    req.request()
    req.asserts()
    req.assert_wanba()
    print(req.host, req.path, req.params, req.error, req.code, req.response.json() if req.code else None)
    print("END")


if __name__ == '__main__':
    planDoneTest()
