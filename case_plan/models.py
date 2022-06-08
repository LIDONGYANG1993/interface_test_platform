import datetime
import json
import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.casePlan.yamlFilersZh import *


# Create your models here


class publicModel(models.Model):
    related_name = "public"
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)  # 创建时间
    updated_time = models.DateTimeField(verbose_name="更新时间", auto_now_add=True)  # 更新时间

    create_user = models.CharField(verbose_name="创建者", max_length=100, blank=True, editable=False)
    update_user = models.CharField(verbose_name="更新者", max_length=100, blank=True, editable=False)
    is_use = models.BooleanField("是否可用", default=True, editable=False, blank=True)

    # 类型选择器
    class typeChoices(models.TextChoices):
        STR = 'STR', _('字符串')
        INT = 'INT', _('数字')
        FLOAT = "FLT", _('浮点')

    # 计算选择器
    class calChoices(models.TextChoices):
        ADD = 'add', _('加')
        SUB = 'subtract', _('减')
        MULT = 'multiply', _('乘')
        DIV = "divide", _('除')

    # 比较选择器
    class funcChoices(models.TextChoices):
        GT = '>', _('大于')
        LT = '<', _('小于')
        EQL = '==', _('等于')
        GTE = '>=', _('大于等')
        LTE = '<=', _('小于等')

    #  请求选择器
    class methodTypeChoices(models.TextChoices):
        POST = "POST", _('POST')
        GET = 'GET', _('GET')

    # 包类选择器
    class appTypeTextChoices(models.TextChoices):
        MAIN = 'MN', _('主包')
        STAR = 'SR', _('星辰')

    # 环境选择器
    class environmentTextChoices(models.TextChoices):
        TEST = 'TEST', _('测试')
        DEV = 'DEV', _('开发')
        PRODUCT = "PRO", _('生产')

    class Meta:
        abstract = True
        ordering = ['created_time', "updated_time"]

    def get_related_name_update_user(self):
        return self.related_name + "update_user"

class defaultModel(publicModel):
    related_name = "default"
    name = models.CharField(configReplace[configFiler.name], max_length=100, default="environment", blank=False)
    value = models.JSONField(configReplace[configFiler.value], max_length=500, default=dict, blank=True)

    def __str__(self):
        return "{}".format(self.name)

class variableModel(publicModel):
    related_name = "variable"
    name = models.CharField(variableReplace[variableFiler.name], max_length=500, default=None, blank=False)  # 变量名称
    plan = models.ForeignKey("planModel", verbose_name=variableReplace[variableFiler.plan], on_delete=models.CASCADE,
                             default=None, blank=True, null=True, editable=False, related_name="variable")
    case = models.ForeignKey("caseModel", verbose_name=variableReplace[variableFiler.case], on_delete=models.CASCADE,
                             default=None, blank=True, null=True, editable=False, related_name="variable_case")
    value = models.CharField(variableReplace[variableFiler.value], max_length=500, default="", blank=False)  # 变量初始值

    class Meta:
        verbose_name = "计划变量"
        verbose_name_plural = "计划变量"

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class extractorModel(publicModel):
    related_name = "extractor"
    step = models.ForeignKey("stepModel", verbose_name=extractorReplace[extractorFiler.step], unique=False,
                             on_delete=models.CASCADE, blank=False, editable=False, null=True)
    step_test = models.ForeignKey("stepModel_test", verbose_name=extractorReplace[extractorFiler.step], unique=False,on_delete=models.SET_NULL, blank=False, editable=False, null=True)
    name = models.CharField(extractorReplace[extractorFiler.name], max_length=100, default="CODE", blank=False)
    value = models.CharField(extractorReplace[extractorFiler.value], max_length=100, default="code", blank=False)
    condition = models.CharField(extractorReplace[extractorFiler.condition], max_length=100, default="", blank=True)
    forDefault = models.CharField("无意义字段【忽略】", max_length=1, default=0, blank=True)  # 该字段无意义，仅为掩盖Djongo的默认不保存缺陷而建立

    class Meta:
        verbose_name = "提取器"
        verbose_name_plural = "提取器"

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class assertsModel(publicModel):
    related_name = "asserts"
    name = models.CharField(assertsReplace[assertsFiler.value1], max_length=100, default="{{CODE}}", blank=False)
    step_test = models.ForeignKey("stepModel_test", verbose_name=assertsReplace[assertsFiler.step], unique=False,
                             on_delete=models.SET_NULL, blank=True, editable=False, null=True)
    step = models.ForeignKey("stepModel", verbose_name=assertsReplace[assertsFiler.step], unique=False,
                             on_delete=models.CASCADE, blank=True, editable=False, null=True)
    case = models.ForeignKey("caseModel", verbose_name=assertsReplace[assertsFiler.case], unique=False,
                             on_delete=models.CASCADE, blank=True, editable=False, null=True)
    func = models.CharField(assertsReplace[assertsFiler.assertMethod], max_length=5,
                            default=publicModel.funcChoices.EQL, choices=publicModel.funcChoices.choices, blank=False)
    name_another = models.CharField(assertsReplace[assertsFiler.value2], max_length=100, default=0, blank=False)

    def __str__(self):
        return "{} {} {}".format(self.name, self.func, self.name_another)

    class Meta:
        verbose_name = "验证器"
        verbose_name_plural = "验证器"


class calculaterModel(publicModel):
    related_name = "calculater"
    name = models.CharField(calculatorReplace[calculatorFiler.name], max_length=100, default="variable0", blank=False)
    step = models.ForeignKey("stepModel", verbose_name=calculatorReplace[calculatorFiler.step], unique=False,on_delete=models.CASCADE)
    stepTest = models.ForeignKey("stepModel_test", verbose_name=calculatorReplace[calculatorFiler.step], unique=False,on_delete=models.SET_NULL, null=True,editable=False)
    value1 = models.CharField(calculatorReplace[calculatorFiler.Variable1], max_length=100, default="{{variable1}}",
                              blank=False)
    func = models.CharField(calculatorReplace[calculatorFiler.calFunction], max_length=10,
                            default=publicModel.calChoices.ADD, choices=publicModel.calChoices.choices, blank=False)
    value2 = models.CharField(calculatorReplace[calculatorFiler.Variable2], max_length=100, default=100, blank=False)

    class Meta:
        verbose_name = "计算器"
        verbose_name_plural = "计算器"

    def __str__(self):
        return "{}：{} {} {}".format(self.name, self.value1, self.func, self.value2)


class requestInfoModel(publicModel):
    related_name = "onStep"
    name = models.CharField(requestInfoReplace[requestInfoFiler.name], max_length=500, default=None, blank=False)
    host = models.CharField(requestInfoReplace[requestInfoFiler.host], max_length=200, default="", blank=True)
    path = models.CharField(requestInfoReplace[requestInfoFiler.path], max_length=200, default="", blank=False)
    method = models.CharField(requestInfoReplace[requestInfoFiler.method], max_length=5,
                              choices=publicModel.methodTypeChoices.choices,
                              default=publicModel.methodTypeChoices.POST)  # 步骤方法,应隶属步骤类型
    headers = models.JSONField(requestInfoReplace[requestInfoFiler.headers], max_length=500, default=dict, blank=True)
    params = models.JSONField(requestInfoReplace[requestInfoFiler.params], max_length=500, default=dict, blank=True)


    class Meta:
        verbose_name = "接口与参数"
        verbose_name_plural = "004-接口与参数"

    def __str__(self):
        return "{}： {}".format(self.name, self.path)


class stepModel(publicModel):
    name = models.CharField(stepReplace[stepFiler.name], max_length=500, default=None, blank=False)
    requestInfo = models.ForeignKey("requestInfoModel", verbose_name=stepReplace[stepFiler.requestInfo], unique=False,on_delete=models.CASCADE)
    params = models.JSONField(stepReplace[stepFiler.reParams], max_length=500, default=dict, blank=True)
    stepNumber = models.IntegerField(stepReplace[stepFiler.stepNumber], default=10001, auto_created=True)

    class Meta:
        verbose_name = "测试步骤"
        verbose_name_plural = "003-接口步骤"
        ordering = ["stepNumber", "name", "updated_time", "created_time"]

    def __str__(self):
        return "{}-{}".format(self.stepNumber, self.name)

    def case_str(self):
        return [rel for rel in self.case.all()]

    case_str.short_description = "所属用例"

class stepModel_test(publicModel):
    name = models.CharField(stepReplace[stepFiler.name], max_length=500, default=None, blank=False)
    requestInfo = models.ForeignKey("requestInfoModel", verbose_name=stepReplace[stepFiler.requestInfo], unique=False,on_delete=models.CASCADE)
    params = models.JSONField(stepReplace[stepFiler.reParams], max_length=500, default=dict, blank=True)
    stepNumber = models.IntegerField(stepReplace[stepFiler.stepNumber], default=10001, auto_created=True)
    case = models.ForeignKey("caseModel", verbose_name=caseReplace[caseFiler.stepList],related_name="step_test",default=None, blank=True, on_delete=models.SET_NULL,null=True)


    class Meta:
        verbose_name = "测试步骤"
        verbose_name_plural = "003-接口步骤"
        ordering = ["stepNumber", "name", "updated_time", "created_time"]

    def __str__(self):
        return "{}-{}".format(self.stepNumber, self.name)

    def case_str(self):
        return self.case.name

    case_str.short_description = "所属用例"

class caseModel(publicModel):
    related_name = "case"
    name = models.CharField(caseReplace[caseFiler.name], max_length=500, default=None, blank=False)
    step = models.ManyToManyField(stepModel, verbose_name=caseReplace[caseFiler.stepList],related_name="case",default=None, blank=True)

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = "002-测试用例"
        default_related_name = "用例集"
        ordering = ["name"]

    def __str__(self):
        return "{}".format(self.name)


    def step_str(self):
        return [rel for rel in self.step.all()]


    step_str.short_description = "步骤"

class planModel(publicModel):
    related_name = "plan"

    name = models.CharField(planReplace[planFiler.name], max_length=500, default=None, blank=False)
    environment_and_type = models.ForeignKey("defaultModel", on_delete=models.SET_NULL, null=True, verbose_name=planReplace[planFiler.environment], max_length=5, default=1)
    case = models.ManyToManyField(caseModel, verbose_name=planReplace[planFiler.caseList], default=None, blank=True)

    class Meta:
        verbose_name = "测试计划"
        verbose_name_plural = "001-测试计划"

    def __str__(self):
        return "{}".format(self.name)


    def val_list_str(self):
        return [rel for rel in self.variable.all().order_by("name")]

    def case_list_str(self):
        return ",\n".join([rel.__str__() for rel in self.case.all().order_by("name")])

    case_list_str.short_description = "用例集合"
    val_list_str.short_description = "变量集合"

class tokenModel(publicModel):
    related_name = "token"
    uid = models.CharField(max_length=100, default=None, blank=False)
    environment = models.CharField(max_length=100, default=None, blank=True, null=True)
    app_type = models.CharField(max_length=100, default=None, blank=True, null=True)
    token = models.JSONField(max_length=100, default=None, blank=True, null=True)