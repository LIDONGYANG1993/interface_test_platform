#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/06/28
# @Name  : 杨望宇
import json

from case_report.core import *
from django.db.models import Model

from case_report.models import *
from config.casePlan.yamlFilersZh import *
from config.logger import Logger, project_path

the_logger = Logger('{}/logs/data/data.log'.format(project_path), 'info', 10, "%(asctime)s-%(message)s").logger

#  所有的类都是从数据库中获取数据，并转化成dict格式，以供对应Done类使用
#  获取数据时，自上而下包含，planData整个计划， caseData单个用例， stepData某个步骤，requestInfoData单接口
#  特殊情况，获取stepData时，同时会获取所属用例的变量，以供单步骤调试使用

# 公共
class publicReportData:
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
class planReportData(publicReportData):
    model_data: planReportModel
    filter = planFiler

    def __init__(self, dataId=None):
        super().__init__(planReportModel, dataId)

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
            self.filter.pass_count: model_data.pass_count,
            self.filter.fail_count: model_data.fail_count,
            self.filter.error_count: model_data.error_count,
            self.filter.msg: model_data.msg,
            public.from_data_id: model_data.from_data.id,
        }

    def get_case_data(self):
        res_data_list = []
        for data_model in self.model_data.casereportmodel_set.filter():
            data_model: caseModel
            res_data_list.append(caseReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_variable_data(self):
        res_data_list = []
        for data_model in self.model_data.variable.filter():
            data_model: variableModel
            res_data_list.append(variableReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_default_data(self):
        defaultReport = defaultReportData()
        defaultReport.get_model(self.model_data.default)
        return defaultReport.data_dict

# 用例
class caseReportData(publicReportData):
    model_data: caseReportModel
    filer = caseFiler

    def __init__(self, dataId=None):
        super().__init__(caseReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET case-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.variable: self.get_variable_data(),
            self.filer.stepList: self.get_step_data(),
            self.filer.assertList: self.get_asserts_data(),
            public.from_data_id: model_data.from_data.id,
            public.is_pass: model_data.is_pass,
            public.msg: model_data.msg.split("\n"),
        }

    def get_variable_data(self):
        res_data_list = []
        for data_model in self.model_data.variable_case.filter():
            data_model: variableModel
            res_data_list.append(variableReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_asserts_data(self):
        res_data_list = []
        for data_model in self.model_data.assertsreportmodel_set.filter():
            data_model: assertsModel
            res_data_list.append(assertReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_step_data(self):
        res_data_list = []
        for data_model in self.model_data.step.filter():
            data_model: stepModel
            res_data_list.append(stepReportData().get_model(data_model).data_dict)
        return res_data_list

    def new_case(self, data_model):
        data_model:caseModel
        self.model_data = data_model

# 步骤
class stepReportData(publicReportData):
    model_data: stepReportModel
    filer = stepFiler

    def __init__(self, dataId=None):
        super().__init__(stepReportData, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.info("GET step-DATA")
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
            public.from_data_id: model_data.from_data.id,
            public.is_pass: model_data.is_pass,
            public.msg: model_data.msg.split("\n"),
            self.filer.status: model_data.status
        }

    def get_requestInfo_data(self):
        variable: variableModel
        requestInfo = requestInfoReportData()
        requestInfo.get_model(self.model_data.requestInfo)
        return requestInfo.data_dict

    def get_asserts_data(self):
        res_data_list = []
        for data_model in self.model_data.assertsreportmodel_set.filter():
            data_model: assertsModel
            res_data_list.append(assertReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_extractor_data(self):
        res_data_list = []
        for data_model in self.model_data.extractorreportmodel_set.filter():
            data_model: extractorModel
            res_data_list.append(extractorReportData().get_model(data_model).data_dict)
        return res_data_list

    def get_calculator_data(self):
        res_data_list = []
        for data_model in self.model_data.calculaterreportmodel_set.filter():
            data_model: calculaterModel
            res_data_list.append(calculaterReportData().get_model(data_model).data_dict)
        return res_data_list

    def request_in_step(self):
        pass

    def get_case_variable(self):
        case_variable = {}
        if self.model_data.case:
            case_data = caseReportData()
            case_data.new_case(self.model_data.case)
            case_variable = case_data.get_variable_data()
        return case_variable


# 单接口
class requestInfoReportData(publicReportData):
    model_data: requestInfoReportModel
    filer = requestInfoFiler

    def __init__(self, dataId=None):
        super().__init__(requestInfoReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET requestInfo-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.host: model_data.host,
            self.filer.path: model_data.path,
            self.filer.params: model_data.params,
            self.filer.method: model_data.method,
            self.filer.headers: model_data.headers,
            self.filer.data: model_data.params,
            self.filer.response: model_data.response,
            self.filer.status: model_data.status,
            public.from_data_id: model_data.from_data.id,
        }

# 变量 -包括计划的变量和用例的变量
class variableReportData(publicReportData):
    model_data: variableReportModel
    filer = variableFiler

    def __init__(self, dataId=None):
        super().__init__(variableReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET variable-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            public.from_data_id: model_data.from_data.id,
        }

# 提取器
class extractorReportData(publicReportData):
    model_data: extractorReportModel
    filer = extractorFiler

    def __init__(self, dataId=None):
        super().__init__(extractorReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            self.filer.condition: model_data.condition,
            self.filer.result:model_data.result,
            public.from_data_id: model_data.from_data.id,
        }

# 计算器
class calculaterReportData(publicReportData):
    model_data: calculaterReportModel
    filer = calculatorFiler

    def __init__(self, dataId=None):
        super().__init__(calculaterReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET calculater-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.Variable1: model_data.value1,
            self.filer.Variable2: model_data.value2,
            self.filer.calFunction: model_data.func,
            self.filer.result: model_data.result,
            public.from_data_id: model_data.from_data.id,

        }

# 验证器
class assertReportData(publicReportData):
    model_data: assertsReportModel
    filer = assertsFiler

    def __init__(self, dataId=None):
        super().__init__(assertsReportModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        return {
            self.filer.dataId: model_data.id,
            self.filer.value1: model_data.name,
            self.filer.value2: model_data.name_another,
            self.filer.assertMethod: model_data.func,
            public.from_data_id: model_data.from_data.id,
            public.is_pass: model_data.is_pass,
            public.msg: model_data.msg.split("\n"),
        }

# 默认数据
class defaultReportData(publicReportData):
    model_data: defaultReportModel_0
    filer = defaultFiler

    def __init__(self, dataId=None):
        super().__init__(defaultReportModel_0, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("default-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.value: model_data.value,
            public.from_data_id: model_data.from_data.id
        }


if __name__ == '__main__':
    res = planReportData(dataId=1)
    print(json.dumps(res.data_dict, ensure_ascii=False))
