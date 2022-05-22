#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/03/14
# @Name  : 杨望宇

from config.casePlan.filers import *

planReplace = {
    planFiler.dataId: "编号",
    planFiler.planName: "计划名称",
    planFiler.environment: "测试环境",
    planFiler.appType: "包类",
    planFiler.globalVariable: "全局变量",
    planFiler.caseList: "用例列表",
    planFiler.isUse: "是否可用",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",

}

caseReplace = {
    caseFiler.caseNumber: "用例编号",
    caseFiler.caseName: "用例名称",
    caseFiler.variable: "局部变量",
    caseFiler.stepList: "步骤列表",
    planFiler.isUse: "是否可用",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",
}

stepReplace = {
    stepFiler.stepNumber: "步骤序号",
    stepFiler.stepFaceName: "步骤名称",
    stepFiler.stepType: "步骤类型",
    stepFiler.interfaceName: "接口名称",
    stepFiler.method: "方法",
    stepFiler.path: "接口请求路径",
    stepFiler.host: "接口请求host",
    stepFiler.interfaceList: "接口id",
    stepFiler.params: "参数集",
    stepFiler.returnData: "变量提取器",
    stepFiler.calculator: "变量计算器",
    stepFiler.assertList: "结果验证器",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",

}

variableReplace = {
    variableFiler.name: "变量名称",
    variableFiler.type: "变量类型",
    variableFiler.value: "值",
    variableFiler.isUse: "是否可用",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",
}


returnDataReplace = {
    resDataFiler.name: "变量名称",
    resDataFiler.type: "变量类型",
    resDataFiler.fieldPath: "提取结果路径",
    resDataFiler.isGlobal: "是否全局",
    resDataFiler.isUse: "是否可用",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",
}


calculatorReplace = {
    calculatorFiler.name: "变量名称",
    calculatorFiler.type: "变量类型",
    calculatorFiler.Variable1: "变量-1",
    calculatorFiler.Variable2: "变量-2",
    calculatorFiler.calFunction: "计算方法",
    calculatorFiler.isGlobal: "是否全局",
    calculatorFiler.isUse: "是否可用",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",
}

assertsReplace = {
    assertsFiler.value1: "验证值-1",
    assertsFiler.assertMethod: "验证方法",
    assertsFiler.value2: "验证值-2",
    assertsFiler.isUse: "是否可用",
    planFiler.dataId: "编号",
    planFiler.createTime: "创建时间",
    planFiler.updateTime: "更新时间",
}
