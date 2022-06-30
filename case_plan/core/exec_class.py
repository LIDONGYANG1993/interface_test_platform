#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇

import datetime
import os.path
import threading
from copy import deepcopy
from config.wanba.interfaceRequest import get_token, app_request
import requests
from requests import Response
from config.casePlan.yamlFilersZh import *
from case_plan.core.func import *
from case_plan.models import publicModel
from config.logger import Logger, project_path
from case_plan.core.read_class import defaultData


asserts_used = []

time_str = str(datetime.datetime.now())
time_str = time_str.replace("-", "_").replace(" ", "__").replace(":", "_").replace(".", "_")
log_path = os.path.join(project_path, "logs", "class", "logs_{}.log".format(time_str))
the_logger = Logger(log_path, 'debug', 10, "%(asctime)s-%(message)s").logger


# 公共的done类
class publicDone:
    def __init__(self, data: dict):
        self.data = data
        self.keys = data.keys()
        self.thread = []

    def _get_value(self, key) -> None or str:
        if key in self.keys:
            return self.data[key]
        return None

    @property
    def get_data_id(self):
        return self._get_value("id")

    @property
    def get_data(self):
        return self._get_value("selfModel")

    def _thread_add(self, func, params=None):
        if params is None: params = []
        thread = threading.Thread(target=func, args=params)
        self.thread.append(thread)

    # 为内部方法提供异步调用
    @staticmethod
    def _thread_run_join(func, params=None):
        if params is None: params = []
        thread = threading.Thread(target=func, args=params)
        thread.start()
        thread.join()

    # 为内部方法提供同步调用
    @staticmethod
    def _run(func, params=None):
        if not params:
            return func()
        return func(params)

    # 从上游数据，提取公共的全局变量
    @staticmethod
    def public_variable(step=None, case=None, plan=None):
        step: stepDone
        case: caseDone
        plan: planDone
        res = {}
        if plan:
            res.update(plan.variable_dict())  # 计划的预置变量
        if case:
            res.update(case.variable_dict())  # 用例的预置变量
            res.update(case.extractor_result)  # 所有步骤下，提取器提取的结果
            res.update(case.calculater_result)  # 所有步骤下，计算器计算的结果
        if step:
            res.update(step.extractor_result)  # 当前步骤下，步骤的提取结果
            res.update(step.calculator_result)  # 当前步骤下，步骤的计算结果
            if not case and step.case_variable:
                res.update(step.case_variable_dict())  # 当前步骤所属的用例下，预置变量
        return res

    # 从data中，完成变量替换
    def variable_replace(self, data, replaceData: dict):
        if isinstance(data, str):  # 字符串类型的替换
            return self.str_replace(data, replaceData)
        if isinstance(data, dict):  # 字典类型的替换
            return self.dict_replace(data, replaceData)
        if isinstance(data, list):  # 字典类型的替换
            return self.list_replace(data, replaceData)

    # 尝试从字符串中找寻替换变量，并完成替换
    @staticmethod
    def str_replace(data, replaceData):
        data_copy = deepcopy(data)
        try:
            data_copy = data_copy.replace("{{", "{").replace("}}", "}")  # 替换格式为"{{}}",并转换为{}
            res = data_copy.format(**replaceData)
        except Exception:
            return data
        return res

    # 尝试从字符串中找寻变量，并完成替换
    def dict_replace(self, data: dict, replaceData):
        for data_key in data.keys():
            data[data_key] = self.variable_replace(data[data_key], replaceData)
        return data

    # 尝试从列表中找寻变量，并完成替换
    def list_replace(self, data: dict, replaceData):
        data_res = []
        for data_key in data:
            data_res.append(self.variable_replace(data_key, replaceData))
        return data_res


#  提取器Done类
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


# 计算器done类
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

    # 计算器 计算方法
    def calculate(self):
        variable1 = self.get_number(self.variable1)
        variable2 = self.get_number(self.variable2)
        if self.calFunction == publicModel.calChoices.ADD:
            return cal.add(variable1, variable2)
        if self.calFunction == publicModel.calChoices.SUB:
            return cal.subtract(variable1, variable2)
        if self.calFunction == publicModel.calChoices.MULT:
            return cal.multiply(variable1, variable2)
        if self.calFunction == publicModel.calChoices.DIV:
            return cal.divide(variable1, variable2)
        return None

    # 直接获取计算结果，如果计算器参数不足或者不规范，则结果为None
    def get_result(self):
        self.replace_in_calculater()  # 计算之前，先进行变量的替换
        self.result = None
        if is_number(self.variable1) and is_number(self.variable2):
            self.result = self.calculate()

    @staticmethod
    def get_number(number):  # 如果数字是整形，则返回整形，否则返回浮点型
        return int(number) if float(number) == int(number) else float(number)

    # 全局变量的替换
    def replace_in_calculater(self):
        self.step: stepDone
        variable = None
        if self.step:
            # 根据级别所在，分别从上游步骤，步骤上游用例，用例上游计划，提取全局变量
            variable = self.public_variable(self.step, self.step.case if self.step.case else None,
                                            self.step.case.plan if self.step.case and self.step.case.plan else None)
        if not variable: return
        self.variable1 = self.variable_replace(self.variable1, variable)
        self.variable2 = self.variable_replace(self.variable2, variable)

    # 返回json格式的计算结果，服务器与API
    def calculater_for_api(self):
        return {
            calculatorFiler.name: self.name,
            calculatorFiler.Variable1: self.variable1,
            calculatorFiler.calFunction: self.calFunction,
            calculatorFiler.Variable2: self.variable2,
            calculatorFiler.result: self.result,
        }


#  验证器Done类
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

        self.msg = ""

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

    #  列出验算算式
    @property
    def get_asserts_str(self):
        if not self.value1 or not self.value2 or not self.assertMethod:
            return None
        if is_number(self.value1) and is_number(self.value2):
            return str(self.value1) + str(self.assertMethod) + str(self.value2)
        return '"{}"'.format(str(self.value1)) + str(self.assertMethod) + '"{}"'.format(str(self.value2))

    @property
    def get_msg(self):
        return self.get_asserts_str + ("失败！" if self.fail else "通过！")

    # 执行字符串代码，直接验算
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

    # 返回json格式的计算结果，服务器与API
    def asserts_result_for_api(self):
        return {
            assertsFiler.value1: self.value1,
            assertsFiler.assertMethod: self.assertMethod,
            assertsFiler.value2: self.value2,
            assertsFiler.assertStr: self.asserts_str,
            assertsFiler.result: self.asserts_result
        }


# 接口信息Done类
class requestDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.token = None
        self.msg = None
        self.name = self.get_name
        self.host = self.get_host
        self.path = self.get_path

        self.headers = self.get_headers.copy()

        self.params = self.get_params.copy()
        self.post_data = self.get_post_data.copy()
        self.method = self.get_method
        self.step = self.get_step

        self.environment = self.get_environment()

        self.response = None
        self.response_json = None
        self.error = None
        self.code = None
        self.status = 10001  # 10001未执行, 10002执行失败, 10003执行异常, 0执行通过


    @property
    def get_name(self):
        return self._get_value(requestInfoFiler.name)

    @property
    def get_params(self):
        return self._get_value(requestInfoFiler.params)

    @property
    def get_post_data(self):
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

    #  全局参数替换
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
        # self.data = self.variable_replace(self.data, variable)
        self.post_data = self.variable_replace(self.post_data, variable)

    # 访问请求
    def request(self):
        the_logger.debug("START-REQUEST,  {}, {}, {}, {}".format(self.name, self.host if self.host else None, self.path,
                                                                 self.params), )

        self.replace_in_requestInfo()  # 访问接口之前，执行参数替换
        get_token(self.params, self.environment)
        if self.host:
            self.request_for_public()  # 如果host存在，不执行环境配置，直接请求
        else:
            self.request_for_wanba()  # 如果有host，执行配置环境
        the_logger.debug("END-REQUEST,  {}, {}, {}, {}".format(self.name, self.host if self.host else None, self.path,
                                                               self.response.json() if self.error is False else None))

    # 玩吧专属的接口请求
    def request_for_wanba(self):
        self.response = app_request(case_url=self.path, params=self.params, environment=self.environment)

    # 通用接口请求
    def request_for_public(self):
        if self.method == "GET":
            self.response = requests.get(url=self.host + self.path, params=self.params, headers=self.headers)
        else:
            self.response = requests.get(url=self.host + self.path, data=self.params, headers=self.headers)

    # 接口请求的校验
    def asserts(self):
        self.response: requests.Response

        if not self.response:  # 校验assert
            self.error = True
            self.status = 10003  # 执行失败，没有返回值
            self.response_json = None
        elif self.response.status_code != 200:  # 校验code
            self.error = True
            self.code = self.response.status_code
            self.status = 10004  # 执行失败，返回code不正常
            self.response_json = None
        elif "__terror" in self.response.json():  # 校验返回值
            self.error = True
            self.status = 10005  # 执行失败，返回值不正确
            self.response_json = None
        else:
            self.error = False
            self.status = 10000  # 执行通过
            try:
                self.response_json = self.response.json()
            except Exception:
                self.status = 10006  # 执行失败，返回值不是json格式

    # 如果玩吧token失效，重新获取token，并重新执行request，仅校验一次
    def assert_wanba(self):
        if self.error is True: return
        if self.response.json()["code"] == 3:
            get_token(self.params, self.environment)
            self.request()
            self.asserts()

    # 返回json格式的结果，服务与API
    def result_for_api(self):
        self.result_massage()
        return {
            requestInfoFiler.name: self.name,
            requestInfoFiler.dataId: self.get_data_id,
            requestInfoFiler.host: self.host,
            requestInfoFiler.path: self.path,
            requestInfoFiler.params: self.params,
            requestInfoFiler.result: self.response_json,
            "msg": self.msg

        }

    # 搜集msg
    def result_massage(self):
        msg = []
        if self.error is None or self.error is True:
            msg.append("接口：{},访问失败！".format(self.name))
        else:
            msg.append("接口：{},访问成功！".format(self.name))
        self.msg = msg

    # 当独立运行requestInfo时，使用配置好的默认环境--此处原本设计为从数据库中读取，暂未实现
    def get_environment(self):
        defaultParams = defaultData(dataId=1).data_dict
        if not self.step: return defaultParams
        if not self.step.case: return defaultParams
        if not self.step.case.plan: return defaultParams
        return self.step.case.plan.default.data


#  变量Done类
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


#  步骤Done类
class stepDone(publicDone):
    response: Response
    calculator_list: [calculaterDone]

    def __init__(self, data):
        super().__init__(data)
        self.msg = None
        self.name = self.get_name
        self.case = self.get_case
        self.stepNumber = self.get_stepNumber
        self.reParams = self.get_reParams.copy()
        self.requestInfo: requestDone = self.get_requestInfo
        self.asserts_list: [assertsDone] = self.get_asserts_list
        self.extractor_list: [extractorDone] = self.get_extractor_list
        self.calculator_list = self.get_calculator_list
        self.case_variable = self.get_case_variable
        self.extractor_result = {}
        self.calculator_result = {}
        self.asserts_result_for_api = []
        self.calculator_result_for_api = []
        self.asserts_result = []
        self.error = None
        self.fail = None
        self.log = []
        self.status = 10001

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
    def get_case_variable(self):
        return self._get_value(stepFiler.case_variable)

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

    #  在步骤中替换参数
    def replace_in_step(self):
        self.case: caseDone
        variable = None
        if self.case:
            variable = self.public_variable(self, self.case, self.case.plan if self.case.plan else None)
        if not variable: return
        self.reParams = self.variable_replace(self.reParams, variable)

    #  在步骤中，实现接口访问
    def request(self):
        self.replace_in_step()
        if self.reParams:  # 当预置了替换参数时，参数会在这里被替换掉
            self.requestInfo.params.update(self.reParams)
        self._thread_run_join(self.requestInfo.request)

    #  接口基本验证
    def asserts_response(self):
        self.requestInfo.asserts()
        self.requestInfo.assert_wanba()
        self.response = self.requestInfo.response
        self.error = self.requestInfo.error
        self.status = self.requestInfo.status

    # 在步骤中，执行提取器
    def extractor_in_step(self):
        for extractor in self.extractor_list:
            extractor: extractorDone
            the_logger.debug("START-EXTRACTOR: {} ".format(extractor.name))
            self._thread_run_join(func=extractor.get_value, params=[self.response.json()])
            the_logger.debug("END-EXTRACTOR: {}--{} ".format(extractor.name, extractor.value))
            self.extractor_result.update({extractor.name: extractor.value})

    # 在步骤中执行计算器
    def calculater_in_step(self):
        for calculater in self.calculator_list:
            calculater: calculaterDone
            the_logger.debug(
                "START-EXTRACTOR: {} {} {}".format(calculater.variable1, calculater.calFunction, calculater.variable2))
            self._thread_run_join(func=calculater.get_result)
            the_logger.debug("START-EXTRACTOR: {} {} {} == {}".format(calculater.variable1, calculater.calFunction,
                                                                      calculater.variable2, calculater.result))
            self.calculator_result.update({calculater.name: calculater.result})
            if calculater.result is None:
                print(self.calculator_result)
            self.calculator_result_for_api.append(calculater.calculater_for_api())

    # 在步骤中执行验证器
    def asserts_in_step(self):
        if len(self.asserts_list) == 0:
            self.fail = False
            return
        for asserts in self.asserts_list:
            if self.fail: return   # 当验证已经失败时，停止继续验证
            asserts: assertsDone
            the_logger.debug("START-ASSERT-CASE: {} ".format(asserts.asserts_str))
            self._thread_run_join(func=asserts.get_result)
            the_logger.debug("END-ASSERT-CASE: {}--{}".format(asserts.asserts_str, asserts.asserts_result))
            if not asserts.asserts_result:  # 步骤的执行结果，遵循验证器的验证结果
                self.fail = True
            else:
                self.fail = False
            self.asserts_result.append(  # 收集验证器的信息
                {assertsFiler.assertStr: asserts.asserts_str, assertsFiler.result: asserts.result})
            self.asserts_result_for_api.append(asserts.asserts_result_for_api())
        return

    # stepDone的特殊方法，如果独立运行step，且step上游case存在变量，字典化以供替换使用
    def case_variable_dict(self):
        res = {}
        for variable in self.case_variable:
            res.update(
                {
                    variable[variableFiler.name]: variable[variableFiler.value]

                }
            )
        return res

    # 执行步骤
    def run_in_step(self):
        self.request()
        self.asserts_response()
        if self.error:  # 当步骤异常时，标记失败，停止提取/计算/验证
            self.fail = True
            return
        self.extractor_in_step()
        self.calculater_in_step()
        self.asserts_in_step()

    # 返回json格式的结果，服务与API
    def result_for_api(self):
        self.result_massage()
        return {
            stepFiler.name: self.name,
            stepFiler.dataId: self.get_data_id,
            stepFiler.stepNumber: self.stepNumber,
            stepFiler.requestInfo: self.requestInfo.result_for_api(),
            stepFiler.extractor: self.extractor_result,
            stepFiler.calculator: self.calculator_result_for_api,
            stepFiler.assertList: self.asserts_result_for_api,
            "msg": self.msg

        }

    #  收集步骤的信息
    def result_massage(self):
        msg = []
        if self.error:
            msg.append("步骤：{},执行异常！".format(self.name))
        elif self.fail is None or self.fail is True:
            msg.append("步骤：{},执行失败！".format(self.name))
        else:
            msg.append("步骤：{},执行成功！".format(self.name))
        for asserts in self.asserts_list:
            if not asserts.asserts_result:
                msg.append("验证：{},验证失败！".format(asserts.asserts_str))
                break
            else:
                msg.append("验证：{}, 验证成功！".format(asserts.asserts_str))
        self.msg = msg


#  用例Done类
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

        self.error = None
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

    # 用例变量的收集，供替换参数使用
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

    # 验证用例结果
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

    #  执行case
    def run_in_case(self):
        for step in self.step_list:
            step: stepDone
            if self.fail: return  # 如果当前步骤异常，停止继续执行，停止验证
            the_logger.debug("START-STEP, {}-{} ".format(step.stepNumber, step.name))
            self._thread_run_join(step.run_in_step), time.sleep(0)
            the_logger.debug("END-STEP, {}-{} ".format(step.stepNumber, step.name))
            self.extractor_result.update(step.extractor_result)
            self.calculater_result.update(step.calculator_result)
            self.step_result_for_api.append(step.result_for_api())
            if not (step.error is False):
                self.error = True
            else:
                self.error = False
            if not (step.error is False) or not (step.fail is False):  # 如果实行失败或者异常，标记用例失败
                self.fail = True
            else:
                self.fail = False
        self.asserts_in_case()  # 正常执行所有步骤之后，进行用例的验证

    #  在本条用例中收集替换参数，以供之后的用例使用
    def get_replace_result(self):
        if self.plan:
            self.plan: planDone
            self.replace_result.update(self.plan.replace_result)
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)
        self.replace_result.update(self.calculater_result)

    # 返回json格式的结果，服务与API
    def result_for_api(self):
        self.result_massage()
        return {
            caseFiler.name: self.name,
            caseFiler.dataId: self.get_data_id,
            caseFiler.stepList: self.step_result_for_api,
            caseFiler.assertList: self.asserts_result_for_api,
            "msg": self.msg
        }

    def result_for_db(self):
        return {
            caseFiler.name: self.name,
            caseFiler.dataId: self.data.get(caseFiler.dataId),
        }

    # 收集用例测msg信息
    def result_massage(self):
        msg = []
        for step in self.step_list:
            step: stepDone
            if not (step.error is False):
                msg.append("步骤：{}-{},执行异常！".format(step.stepNumber, step.name))
                break
            elif not (step.fail is False):
                msg.append("步骤：{}-{},执行失败！".format(step.stepNumber, step.name))
                break
            else:
                msg.append("步骤：{}-{},执行成功！".format(step.stepNumber, step.name))
        for asserts in self.asserts_list:
            if not (asserts.fail is False):
                msg.append("验证：{},验证失败！".format(asserts.asserts_str))
                break
            else:
                msg.append("验证：{}, 验证成功！".format(asserts.asserts_str))
        self.msg = msg

class defaultDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.value = self.get_value

    @property
    def get_name(self):
        return self._get_value(configReplace[default.name])

    @property
    def get_value(self):
        return self._get_value(configReplace[default.value])




# 计划Done类
class planDone(publicDone):
    def __init__(self, data):
        super().__init__(data)
        self.name = self.get_name
        self.variable = self.get_variable
        self.default = self.get_default
        self.extractor_result = {}
        self.calculater_result = {}
        self.replace_result = {}
        self.case_result_for_api = []
        self.case_list = self.get_case_list

        self.error_list = []
        self.pass_list = []
        self.fail_list = []

        self.msg = None

    @property
    def get_variable(self):
        parents = {variableFiler.plan: self, variableFiler.case: None}
        return make_class_list(self._get_value(planFiler.globalVariable), variableDone, variableFiler.used, parents)

    @property
    def get_name(self):
        return self._get_value(planFiler.name)

    @property
    def get_default(self):
        parents = {default.plan: self}
        return make_class(self._get_value(planFiler.environment), defaultDone, default.used, parents)

    @property
    def get_case_list(self):
        parents = {caseFiler.plan: self}
        return make_class_list(self._get_value(planFiler.caseList), caseDone, caseFiler.used, parents)

    #  执行
    def run_in_plan(self):
        the_logger.debug("START-PLAN")

        for case in self.case_list:
            case: caseDone

            the_logger.debug("START-CASE: {} ".format(case.name))
            self._thread_run_join(case.run_in_case)
            the_logger.debug("END-CASE: {} ".format(case.name, not case.fail))
            self.extractor_result.update(case.extractor_result)
            result = case.result_for_db()
            self.case_result_for_api.append(case.result_for_api())
            if case.error: self.error_list.append(result)
            elif case.fail: self.fail_list.append(result)
            else: self.pass_list.append(result)
        the_logger.debug("END-PLAN")

    # 收集替换参数
    def get_replace_result(self):
        for var in self.variable:
            self.replace_result.update(var)
        self.replace_result.update(self.extractor_result)


    def get_error_count(self):
        return len(self.error_list)

    def get_fail_count(self):
        return len(self.fail_list)

    def get_pass_count(self):
        return len(self.pass_list)

    # 返回json格式的结果，服务与API
    def result_for_api(self):
        self.result_massage()
        return {
            planFiler.name: self.name,
            planFiler.dataId: self.get_data_id,
            planFiler.environment: self.default,
            planFiler.caseList: self.case_result_for_api,
            "msg": self.msg

        }

    # 收集msg
    def result_massage(self):
        msg = []
        for case in self.case_list:
            case: caseDone
            if not (case.fail is False):
                msg.append("用例：{},执行失败！".format(case.name))
            else:
                msg.append("用例：{},执行成功！".format(case.name))
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
    from case_plan.core.read_class import assertData
    asserts = assertsDone(assertData(1).data_dict)
    asserts.get_result()
    print(asserts.asserts_str)


def planDoneTest():
    from case_plan.core.read_class import planData
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
