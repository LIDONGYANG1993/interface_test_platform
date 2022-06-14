#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/03/14
# @Name  : 杨望宇



class databaseYAPI:
    GROUP = 'yapi_group'
    PROJECT = 'yapi_project'
    CAT = 'yapi_cat'
    INTERFACE = 'yapi_interface'
    CASE = 'auto_case'


class databaseCase:
    interface_data_plan = "interface_data_plan"
    interface_data_case = "interface_data_case"
    interface_data_variable = "interface_data_variable"
    interface_data_step = "interface_data_step"
    interface_data_resData = "interface_data_resData"
    interface_data_calculator = "interface_data_calculator"
    interface_data_asserts = "interface_data_asserts"
    interface_data_configFilers = "interface_data_configFilers"
    interface_data_interface = "interface_data_interface"


    stepType = "stepType"
    valueType = "valueType"

    dataId = "_id"
    DataId = "dataId"


class configValue:
    name = "name"
    value_cn = "value_cn"


class filersYAPI:
    id = "_id"
    cat_id = "cat_id"
    interface_id = "interface_id"
    project_id = "project_id"
    group_id = "group_id"
    is_update = "is_update"
    is_cover = "is_cover"


class mangoDone:
    set = "$set"  # 修改数据 操作符
    type = "$type"  # 类型查询 操作符

    regex = "$regex"  # 正则查询 操作符
    greaterThan = "$gt"  # 大于符
    lessThan = "$lt"  # 小于符
    greaterThanEqual = "$gte"  # 大于等于符
    lessThanEqual = "$lte"  # 小于等于符


class variableFiler:
    name = "name"  # 变量名称
    type = "type"  # 变量类型
    value = "value"  # 变量初始值
    plan = "plan"  # 所属计划
    case = "case"  # 所属用例


    used = [name, value, plan, case]

    dataId = "id"
    isUse = "isUse"


class planFiler:
    name = "name"  # 计划名称
    environment = "environment"  # 环境
    appType = "appType"  # 包类
    globalVariable = "globalVariable"  # 全局变量 所有的变量，会在每次执行该计划时，初始化
    caseList = "caseList"  # 场景用例列表


    dataId = "id"
    isUse = "isUse"
    createTime = "createTime"
    updateTime = "updateTime"


class caseFiler:
    caseNumber = "caseNumber"  # 场景用例编号
    name = "name"  # 用例名称
    model = "model"  # 所属模块
    variable = "variable"  # 局部变量
    stepList = "stepList"  # 步骤列表

    plan = "plan"
    assertList = "assertList"

    used = [name, variable, stepList, plan, assertList]

    dataId = "id"
    isUse = "isUse"
    createTime = "createTime"
    updateTime = "updateTime"


class stepFiler:
    name = "name"  # 步骤名称
    stepNumber = "stepNumber"  # 步骤编号，考虑是否自动生成

    requestInfo = "requestInfo"

    case = "case"

    reParams = "reParams"  # 替换参数
    extractor = "extractor"  # 提取器
    calculator = "calculator"  # 计算器
    assertList = "assertList"  # 验证器
    case_variable = "case_variable"  # 验证器

    used = [name, stepNumber, requestInfo, reParams, extractor, calculator, assertList, case]


    isUse = "isUse"
    dataId = "id"
    createTime = "createTime"
    updateTime = "updateTime"


class requestInfoFiler:
    name = "name"  # 接口名称
    host = "host"
    path = "path"

    method = "method"  # 请求方法
    params = "params"  # 参数
    doc_url = "params"  # 参数

    headers = "headers"
    data = "data"
    result = "result"

    step = "step"
    dataId = "id"

    used = [name, host, path, headers, method, params, data, step]


class interfaceFiler:
    # 接口信息，为None时，表示无法解析页面，需要确认页面
    interface_id = "interface_id"  # 接口id
    name = 'name'  # 名称
    path = 'path'  # url路径
    method = 'method'  # 请求方法
    headers = "headers"  # 请求头
    body = "body"  # 请求参数
    stepList = "stepList"  # 这个接口被用于哪些步骤
    caseList = "caseList"  # 这个接口被哪些场景覆盖
    isUse = "isUse"




    dataId = "id"
    createTime = "createTime"
    updateTime = "updateTime"




class extractorFiler:
    name = "name"  # 提取器存储名称，
    step = "step"  # 提取器存储名称，
    value = "value"   # 提取路径参数，返回值是json格式的情况，采用A.b.c.0.d的方法，提取数值，
    condition = "condition"

    used = [name, value, condition, step]

    isUse = "isUse"
    dataId = "id"


class calculatorFiler:
    name = "name"  # 提取器存储名称，
    Variable1 = "Variable1"  # 变量1
    Variable2 = "Variable2"  # 变量2
    step = "step"
    calFunction = "calFunction"  # 计算方式，add , subtract , multiply  divide  对应，+ - * ÷

    used = [name, Variable1, Variable2, calFunction, step]

    result = "result"

    isUse = "isUse"
    dataId = "id"
    createTime = "createTime"
    updateTime = "updateTime"

class configFiler:
    name = "name"  # 提取器存储名称，
    value = "value"  # 变量1
    isUse = "isUse"
    dataId = "id"
    createTime = "createTime"
    updateTime = "updateTime"



class assertsFiler:
    value1 = "value1"  # 验证变量名称1，可以引用全局变量，或者局部变量，也可以输入值；
    assertMethod = "assertMethod"  # 验证方法，如果变量，是数字，可选方法 gt lt equal 对应大于， 等于，小于, 如果变量是类型，可选方法 is，in， not_in 对应相同，
    step = "step"
    case = "case"
    value2 = "value2"  # 验证变量名称2，可以引用全局变量，或者局部变量，也可以输入值；

    used = [value1, assertMethod, value2, step, case]

    result = "result"
    assertStr = "assertStr"

    isUse = "isUse"
    dataId = "id"
    createTime = "createTime"
    updateTime = "updateTime"



