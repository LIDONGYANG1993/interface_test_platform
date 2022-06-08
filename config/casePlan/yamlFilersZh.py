#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/03/14
# @Name  : 杨望宇

from config.casePlan.filers import *

planReplace = {
    planFiler.name: "计划名称",
    planFiler.environment: "测试环境",
    planFiler.appType: "包类",
    planFiler.globalVariable: "全局变量",
    planFiler.caseList: "用例列表",

    planFiler.dataId: "编号",
    planFiler.isUse: "是否可用",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",

}

caseReplace = {
    caseFiler.caseNumber: "用例编号",
    caseFiler.name: "用例名称",
    caseFiler.variable: "局部变量",
    caseFiler.stepList: "步骤列表",
    caseFiler.model: "所属模块",

    caseFiler.isUse: "是否可用",
    caseFiler.dataId: "编号"
}

stepReplace = {
    stepFiler.stepNumber: "步骤序号",
    stepFiler.name: "步骤名称",
    stepFiler.case: "所属用例",


    stepFiler.requestInfo: "接口访问信息",
    stepFiler.reParams: "替换参数",


    stepFiler.extractor: "变量提取器",
    stepFiler.calculator: "变量计算器",
    stepFiler.assertList: "结果验证器",

    stepFiler.dataId: "编号"

}

requestInfoReplace= {
    requestInfoFiler.name: "接口名称",
    requestInfoFiler.method: "方法",
    requestInfoFiler.path: "接口请求路径",
    requestInfoFiler.host: "接口请求host",
    requestInfoFiler.params: "默认参数",
    requestInfoFiler.headers: "headers",
    stepFiler.dataId: "编号"
}

variableReplace = {
    variableFiler.name: "变量名称",
    variableFiler.type: "变量类型",
    variableFiler.value: "值",
    variableFiler.plan: "所属计划",
    variableFiler.case: "所属用例",

    variableFiler.isUse: "是否可用",
    variableFiler.dataId: "编号"
}


extractorReplace = {
    extractorFiler.name: "变量名称",
    extractorFiler.value: "提取内容",
    extractorFiler.condition: "提取条件",
    extractorFiler.step: "所属步骤",

    extractorFiler.isUse: "是否可用",
    extractorFiler.dataId: "编号"
}


calculatorReplace = {
    calculatorFiler.step: "所属步骤",
    calculatorFiler.name: "变量名称",
    calculatorFiler.Variable1: "变量-1",
    calculatorFiler.Variable2: "变量-2",
    calculatorFiler.calFunction: "计算方法",

    calculatorFiler.isUse: "是否可用",
    calculatorFiler.dataId: "编号"
}

assertsReplace = {
    assertsFiler.value1: "验证值-1",
    assertsFiler.assertMethod: "验证方法",
    assertsFiler.value2: "验证值-2",
    assertsFiler.step: "所属步骤",
    assertsFiler.case: "所属用例",

    assertsFiler.isUse: "是否可用",
    assertsFiler.dataId: "编号",
}

configReplace = {

    configFiler.name: "配置参数名称",
    configFiler.value: "配置值",
    configFiler.isUse: "是否可用",
    configFiler.dataId: "编号",
}