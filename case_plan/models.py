import datetime
import json
import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.casePlan.yamlFilersZh import *
from django.contrib.auth.models import AbstractUser

# Create your models here


class publicModel(models.Model):

    related_name = "public"
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now=True)  # 创建时间
    updated_time = models.DateTimeField(verbose_name="更新时间", auto_now_add=True)  # 更新时间
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="创建者", unique=False, on_delete=models.CASCADE,blank=True,editable=False)
    update_user = models.CharField(verbose_name="更新者",max_length=100,blank=True,editable=False)
    is_use = models.BooleanField("是否可用", default=True, editable=False,blank=True)

    # 类型选择器
    class typeChoices(models.TextChoices):
        STR = 'STR', _('字符串')
        INT = 'INT', _('数字')
        FLOAT = "FLT", _('浮点')

    # 计算选择器
    class calChoices(models.TextChoices):
        ADD = 'add', _('加')
        SUB = 'sub', _('减')
        MULT = 'mult', _('乘')
        DIV = "div", _('除')

    # 比较选择器
    class funcChoices(models.TextChoices):
        GT = '>', _('大于')
        LT = '<', _('小于')
        EQL = '=', _('等于')
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



class variable(publicModel):
    related_name = "variable"
    name = models.CharField(variableReplace[variableFiler.name],max_length=500, default=None, blank=False)  # 变量名称
    plan = models.ForeignKey("plan",verbose_name=variableReplace[variableFiler.plan], on_delete=models.CASCADE, default=None, blank=True)
    value = models.CharField(variableReplace[variableFiler.value],max_length=500, default="", blank=False)  # 变量初始值

    class Meta:
        verbose_name = "计划变量"
        verbose_name_plural = "计划变量"



    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class response(publicModel):
    related_name = "response"
    step = models.ForeignKey("step", verbose_name=responseReplace[responseFiler.step], unique=False, on_delete=models.CASCADE, auto_created=True, blank=True)
    name = models.CharField(responseReplace[responseFiler.name], max_length=100, default="CODE", blank=False)
    value = models.CharField(responseReplace[responseFiler.fieldPath], max_length=100, default="code", blank=False)

    class Meta:
        verbose_name = "提取器"
        verbose_name_plural = "提取器"

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class asserts(publicModel):
    related_name = "asserts"
    name = models.CharField(assertsReplace[assertsFiler.value1], max_length=100, default="{{CODE}}", blank=False)
    step = models.ForeignKey("step", verbose_name=assertsReplace[assertsFiler.step],unique=False, on_delete=models.CASCADE)
    func = models.CharField(assertsReplace[assertsFiler.assertMethod], max_length=5, default=publicModel.funcChoices.EQL, choices=publicModel.funcChoices.choices, blank=False)
    name_another = models.CharField(assertsReplace[assertsFiler.value2], max_length=100, default=0, blank=False)

    def __str__(self):
        return "{} {} {}".format(self.name, self.func, self.name_another)

    class Meta:
        verbose_name = "验证器"
        verbose_name_plural = "验证器"


class calculater(publicModel):
    related_name = "calculater"
    name = models.CharField(calculatorReplace[calculatorFiler.name], max_length=100, default="variable0", blank=False)
    step = models.ForeignKey("step",verbose_name=calculatorReplace[calculatorFiler.step], unique=False, on_delete=models.CASCADE)
    value1 = models.CharField(calculatorReplace[calculatorFiler.Variable1], max_length=100, default="{{variable1}}", blank=False)
    func = models.CharField(calculatorReplace[calculatorFiler.calFunction], max_length=5, default=publicModel.calChoices.ADD, choices=publicModel.calChoices.choices, blank=False)
    value2 = models.CharField(calculatorReplace[calculatorFiler.Variable2], max_length=100, default="100", blank=False)

    class Meta:
        verbose_name = "计算器"
        verbose_name_plural = "计算器"

    def __str__(self):
        return "{}：{} {} {}".format(self.name, self.value1, self.func, self.value2)


class onStep(publicModel):
    related_name = "onStep"

    name = models.CharField(stepReplace[stepFiler.interfaceName], max_length=500, default=None, blank=False)
    host = models.CharField(stepReplace[stepFiler.host], max_length=200, default="", blank=True)
    path = models.CharField(stepReplace[stepFiler.path], max_length=200, default="", blank=False)
    method = models.CharField(stepReplace[stepFiler.method], max_length=5, choices=publicModel.methodTypeChoices.choices,
                              default=publicModel. methodTypeChoices.POST)  # 步骤方法,应隶属步骤类型
    params = models.JSONField(stepReplace[stepFiler.params], max_length=500, default=dict, blank=True)


    class Meta:
        verbose_name = "接口与参数"
        verbose_name_plural = "接口与具体参数"

    def __str__(self):
        return "{}： {}".format(self.name, self.path)


class step(publicModel):
    related_name = "step"
    name = models.CharField(stepReplace[stepFiler.stepName], max_length=500, default=None, blank=False)
    onStep = models.ForeignKey("onStep", verbose_name=stepReplace[stepFiler.requestInfo], unique=False, on_delete=models.CASCADE)
    stepNumber = models.IntegerField(stepReplace[stepFiler.stepNumber], default=10001, auto_created=True)

    class Meta:
        verbose_name = "测试步骤"
        verbose_name_plural = "003-接口步骤"
        ordering = ["stepNumber", "name", "updated_time", "created_time"]

    def __str__(self):
        return "{}-{}".format(self.stepNumber, self.name)


class case(publicModel):
    related_name = "case"
    name = models.CharField(caseReplace[caseFiler.caseName], max_length=500, default=None, blank=False)
    step = models.ManyToManyField(step, verbose_name=caseReplace[caseFiler.stepList], default=None, blank=True)

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = "002-测试用例"
        default_related_name = "用例集"

        ordering = ["name"]

    def __str__(self):
        return "{}".format(self.name)


class plan(publicModel):
    related_name = "plan"

    name = models.CharField(planReplace[planFiler.planName], max_length=500, default=None, blank=False)
    environment = models.CharField(planReplace[planFiler.environment], max_length=5,choices=publicModel.environmentTextChoices.choices, default=publicModel.environmentTextChoices.TEST)
    app_type = models.CharField(planReplace[planFiler.appType], max_length=5, choices=publicModel.appTypeTextChoices.choices,default=publicModel.appTypeTextChoices.MAIN)
    case = models.ManyToManyField(case, verbose_name=planReplace[planFiler.caseList], default=None, blank=True)

    class Meta:
        verbose_name = "测试计划"
        verbose_name_plural = "001-测试计划"

    def __str__(self):
        return "{}".format(self.name)
