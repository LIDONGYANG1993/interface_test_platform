#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/27
# @Name  : 杨望宇
import json

from case_plan.core import *
from django.db.models import Model

from case_plan.models import *
from config.casePlan.yamlFilersZh import *
from config.logger import Logger, project_path

the_logger = Logger('{}/logs/data/data.log'.format(project_path), 'info', 10, "%(asctime)s-%(message)s").logger

#  所有的类都是从数据库中获取数据，并转化成dict格式，以供对应Done类使用
#  获取数据时，自上而下包含，planData整个计划， caseData单个用例， stepData某个步骤，requestInfoData单接口
#  特殊情况，获取stepData时，同时会获取所属用例的变量，以供单步骤调试使用

# 公共
class publicData:
    def __init__(self, model: Model, dataId=None, name=None):
        self.model = model
        self.dataId = dataId
        self.name = name

        self.model_data = self.get_by_id()
        self.data_dict = self.get_data()

    def get_by_id(self):
        if not self.dataId:
            return None
        return self.model.objects.get(id=self.dataId)

    def get_by_name(self):
        if not self.name:
            return None
        return self.model.objects.get(name=self.name)

    def filter_by_id(self):
        return self.model.objects.filter(id=self.dataId)

    def get_data(self):
        pass

    def get_model(self, model):
        self.model_data = model
        self.data_dict = self.get_data()
        return self

# 计划
class planData(publicData):
    model_data: planModel
    filter = planFiler

    def __init__(self, dataId=None):
        super().__init__(planModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET PLAN-DATA")
        return {
            self.filter.dataId: model_data.id,
            self.filter.caseList: self.get_case_data(),
            self.filter.name: model_data.name,
            self.filter.environment: self.get_default_data(),
            self.filter.globalVariable: self.get_variable_data(),
            "selfModel":self
        }

    def get_case_data(self):
        res_data_list = []
        for data_model in self.model_data.case.filter():
            data_model: caseModel
            res_data_list.append(caseData().get_model(data_model).data_dict)
        return res_data_list

    def get_variable_data(self):
        res_data_list = []
        for data_model in self.model_data.variable_plan.filter():
            data_model: variableModel
            res_data_list.append(variableData().get_model(data_model).data_dict)
        return res_data_list

    def get_default_data(self):
        return defaultData(self.model_data.default.id).data_dict

# 用例
class caseData(publicData):
    model_data: caseModel
    filer = caseFiler

    def __init__(self, dataId=None):
        super().__init__(caseModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.info("GET CASE-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.variable: self.get_variable_data(),
            self.filer.stepList: self.get_step_data(),
            self.filer.assertList: self.get_asserts_data(),
            "selfModel":self
        }

    def get_variable_data(self):
        res_data_list = []
        for data_model in self.model_data.variable_case.filter():
            data_model: variableModel
            res_data_list.append(variableData().get_model(data_model).data_dict)
        return res_data_list

    def get_asserts_data(self):
        res_data_list = []
        for data_model in self.model_data.assertsmodel_set.filter():
            data_model: assertsModel
            res_data_list.append(assertData().get_model(data_model).data_dict)
        return res_data_list

    def get_step_data(self):
        res_data_list = []
        for data_model in self.model_data.step.filter():
            data_model: stepModel
            res_data_list.append(stepData().get_model(data_model).data_dict)
        return res_data_list

    def new_case(self, data_model):
        data_model:caseModel
        self.model_data = data_model

# 步骤
class stepData(publicData):
    model_data: stepModel
    filer = stepFiler

    def __init__(self, dataId=None):
        super().__init__(stepModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET STEP-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.reParams: model_data.params,
            self.filer.stepNumber: model_data.stepNumber,
            self.filer.requestInfo: self.get_requestInfo_data(),
            self.filer.assertList: self.get_asserts_data(),
            self.filer.calculator: self.get_calculator_data(),
            self.filer.extractor: self.get_extractor_data(),
            self.filer.case_variable: self.get_case_variable(),
            "selfModel":self
        }

    def get_requestInfo_data(self):
        variable: variableModel
        return requestInfoData(dataId=self.model_data.requestInfo.id).data_dict

    def get_asserts_data(self):
        res_data_list = []
        for data_model in self.model_data.assertsmodel_set.filter():
            data_model: assertsModel
            res_data_list.append(assertData().get_model(data_model).data_dict)
        return res_data_list

    def get_extractor_data(self):
        res_data_list = []
        for data_model in self.model_data.extractormodel_set.filter():
            data_model: extractorModel
            res_data_list.append(extractorData().get_model(data_model).data_dict)
        return res_data_list

    def get_calculator_data(self):
        res_data_list = []
        for data_model in self.model_data.calculatermodel_set.filter():
            data_model: calculaterModel
            res_data_list.append(calculaterData().get_model(data_model).data_dict)
        return res_data_list

    def request_in_step(self):
        pass

    def get_case_variable(self):
        case_variable = {}
        if self.model_data.case:
            case_data = caseData()
            case_data.new_case(self.model_data.case)
            case_variable = case_data.get_variable_data()
        return case_variable

# 单接口
class requestInfoData(publicData):
    model_data: requestInfoModel
    filer = requestInfoFiler

    def __init__(self, dataId=None):
        super().__init__(requestInfoModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET REQUEST-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.host: model_data.host,
            self.filer.path: model_data.path,
            self.filer.params: model_data.params,
            self.filer.method: model_data.method,
            self.filer.headers: model_data.headers,
            self.filer.data: model_data.params,
            "selfModel":self
        }

# 变量 -包括计划的变量和用例的变量
class variableData(publicData):
    model_data: variableModel
    filer = variableFiler

    def __init__(self, dataId=None):
        super().__init__(variableModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET VAR-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            "selfModel":self
        }

# 提取器
class extractorData(publicData):
    model_data: extractorModel
    filer = extractorFiler

    def __init__(self, dataId=None):
        super().__init__(extractorModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET EXT-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            self.filer.condition: model_data.condition,
            "selfModel":self
        }

# 计算器
class calculaterData(publicData):
    model_data: calculaterModel
    filer = calculatorFiler

    def __init__(self, dataId=None):
        super().__init__(calculaterModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET CALC-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.Variable1: model_data.value1,
            self.filer.Variable2: model_data.value2,
            self.filer.calFunction: model_data.func,
            "selfModel":self
        }

# 验证器
class assertData(publicData):
    model_data: assertsModel
    filer = assertsFiler

    def __init__(self, dataId=None):
        super().__init__(assertsModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        return {
            self.filer.dataId: model_data.id,
            self.filer.value1: model_data.name,
            self.filer.value2: model_data.name_another,
            self.filer.assertMethod: model_data.func,
            "selfModel":self
        }

# 默认数据
class defaultData(publicData):
    model_data: defaultModel
    filer = defaultFiler

    def __init__(self, dataId=None):
        super().__init__(defaultModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET CONFIG-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            "selfModel":self
        }

# token表
class tokenData(publicData):
    model_data: tokenModel
    model: tokenModel

    def __init__(self,uid, app_type, environment):
        super().__init__(tokenModel)
        self.model_data = self.get_by_filed(uid, app_type, environment)

    def get_by_filed(self, uid, app_type, environment):
        return self.model.objects.get(uid=uid, app_type=app_type, environment=environment)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET CONFIG-DATA")
        return {
            "dataId": model_data.id,
            "uid": model_data.uid,
            "token": model_data.token,
            "selfModel":self
        }



if __name__ == '__main__':
    res = planData(dataId=1)
    print(json.dumps(res.data_dict, ensure_ascii=False))
