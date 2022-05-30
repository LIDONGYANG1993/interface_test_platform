#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/27
# @Name  : 杨望宇
import json

from case_plan.core import *
from django.db.models import Model

from case_plan.models import *
from config.casePlan.yamlFilersZh import *
from config.logger import Logger,project_path

the_logger = Logger('{}/logs/data/data.log'.format(project_path), 'debug', 10, "%(asctime)s-%(message)s").logger

class publicData:
    def __init__(self, model: Model, dataId=None):
        self.model = model
        self.dataId = dataId


        self.model_data = self.get_by_id()
        self.data_dict = self.get_data()

    def get_by_id(self):
        return self.model.objects.get(id=self.dataId)

    def filter_by_id(self):
        return self.model.objects.filter(id=self.dataId)

    def get_data(self):
        pass

class planData(publicData):
    model_data: planModel
    filter = planFiler

    def __init__(self, dataId):
        super().__init__(planModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None
        the_logger.info("GET PLAN-DATA")
        return {
            self.filter.dataId:model_data.id,
            self.filter.caseList:self.get_case_data(),
            self.filter.name: model_data.name,
            self.filter.environment:model_data.environment,
            self.filter.globalVariable:self.get_variable_data()
        }


    def get_case_data(self):
        res_data_list = []
        for case in self.model_data.case.filter():
            case:caseModel
            res_data_list.append(caseData(dataId=case.id).data_dict)
        return res_data_list

    def get_variable_data(self):
        res_data_list = []
        for variable in self.model_data.variable.filter():
            variable: variableModel
            res_data_list.append(variableData(dataId=variable.id).data_dict)
        return res_data_list

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
            self.filer.dataId:model_data.id,
            self.filer.name:model_data.name,
            self.filer.variable:self.get_variable_data(),
            self.filer.stepList:self.get_step_data(),
            self.filer.assertList:self.get_asserts_data(),
            # self.filer.caseNumber:the_model.caseNumber,
        }

    def get_variable_data(self):
        res_data_list = []
        for variable in self.model_data.variable_case.filter():
            variable: variableModel
            res_data_list.append(variableData(dataId=variable.id).data_dict)
        return res_data_list

    def get_asserts_data(self):
        res_data_list = []
        for variable in self.model_data.assertsmodel_set.filter():
            variable: variableModel
            res_data_list.append(assertData(dataId=variable.id).data_dict)
        return res_data_list

    def get_step_data(self):
        res_data_list = []
        for variable in self.model_data.step.filter():
            variable: variableModel
            res_data_list.append(stepData(dataId=variable.id).data_dict)
        return res_data_list




class variableData(publicData):
    model_data: variableModel
    filer = variableFiler

    def __init__(self, dataId):
        super().__init__(variableModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET VAR-DATA")
        return {
            self.filer.dataId:model_data.id,
            self.filer.name: model_data.name,
            self.filer.value:model_data.value
        }


class stepData(publicData):
    model_data: stepModel
    filer = stepFiler

    def __init__(self, dataId):
        super().__init__(stepModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET STEP-DATA")
        return {
            self.filer.dataId:model_data.id,
            self.filer.name: model_data.name,
            self.filer.reParams: model_data.params,
            self.filer.stepNumber: model_data.stepNumber,
            self.filer.requestInfo:  self.get_requestInfo_data(),
            self.filer.assertList: self.get_asserts_data(),
            self.filer.calculator: self.get_calculator_data(),
            self.filer.extractor: self.get_extractor_data(),
        }

    def get_requestInfo_data(self):
        variable: variableModel
        return requestInfoData(dataId=self.model_data.requestInfo.id).data_dict

    def get_asserts_data(self):
        res_data_list = []
        for variable in self.model_data.assertsmodel_set.filter():
            variable: variableModel
            res_data_list.append(assertData(dataId=variable.id).data_dict)
        return res_data_list

    def get_extractor_data(self):
        res_data_list = []
        for variable in self.model_data.extractormodel_set.filter():
            variable: extractorModel
            res_data_list.append(extractorData(dataId=variable.id).data_dict)
        return res_data_list

    def get_calculator_data(self):
        res_data_list = []
        for variable in self.model_data.calculatermodel_set.filter():
            variable: variableModel
            res_data_list.append(calculaterData(dataId=variable.id).data_dict)
        return res_data_list


class requestInfoData(publicData):
    model_data: requestInfoModel
    filer = requestInfoFiler

    def __init__(self, dataId):
        super().__init__(requestInfoModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET REQUEST-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.name: model_data.name,
            self.filer.host:model_data.host,
            self.filer.path:model_data.path,
            self.filer.params:model_data.params,
            self.filer.method:model_data.method,
            self.filer.headers:model_data.params,
            self.filer.data:model_data.params,
        }

class extractorData(publicData):
    model_data: extractorModel
    filer = extractorFiler

    def __init__(self, dataId):
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
        }

class calculaterData(publicData):
    model_data: calculaterModel
    filer = calculatorFiler

    def __init__(self, dataId):
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
        }

class assertData(publicData):
    model_data: assertsModel
    filer = assertsFiler

    def __init__(self, dataId):
        super().__init__(assertsModel, dataId)

    def get_data(self):
        model_data = self.model_data
        if not model_data: return None

        the_logger.debug("GET ASSERT-DATA")
        return {
            self.filer.dataId: model_data.id,
            self.filer.value1: model_data.name,
            self.filer.value2: model_data.name_another,
            self.filer.assertMethod: model_data.func
        }




if __name__ == '__main__':
    res = planData(dataId=1)
    print(json.dumps(res.data_dict,ensure_ascii=False))
    pass
