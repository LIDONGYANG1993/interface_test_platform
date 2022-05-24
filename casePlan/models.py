import datetime
import time

from django.db import models
import mongoengine
from django.utils.translation import gettext_lazy as _

from config.casePlan.yamlFilersZh import *


# Create your models here


class variableModel(models.Model):
    class typeChoices(models.TextChoices):
        STR = 'STR', _('字符串')
        INT = 'INT', _('数字')
        FLOAT = "FLT", _('浮点')


    name = models.CharField(max_length=500, default=None, blank=False)  # 变量名称
    plan = models.ForeignKey("planModel",on_delete=models.CASCADE,default=None,blank=True)
    value = models.CharField(max_length=500, default="", blank=False)  # 变量初始值
    isUse = models.BooleanField(default=True)



    class Meta:
        verbose_name = "计划变量"
        verbose_name_plural = "计划变量"

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class responseModel(models.Model):

    name = models.CharField("变量名称", max_length=100, default="CODE",blank=False)
    step = models.ForeignKey("stepModel",unique=False, on_delete=models.CASCADE, auto_created=True)
    value = models.CharField("提取参数", max_length=100, default="code", blank=False)


    class Meta:
        verbose_name = "提取器"
        verbose_name_plural = "提取器"

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class assertModel(models.Model):
    class funcChoices(models.TextChoices):
        GT = '>', _('大于')
        LT = '<', _('小于')
        EQL = '=', _('等于')
        GTE = '>=', _('大于等')
        LTE = '<=', _('小于等')

    name = models.CharField("变量名称", max_length=100, default="{{CODE}}",blank=False)
    step = models.ForeignKey("stepModel",unique=False, on_delete=models.CASCADE, auto_created=True)
    func = models.CharField("计算方法", max_length=5, default=funcChoices.EQL, choices=funcChoices.choices,blank=False)
    value = models.CharField("验证值", max_length=100, default=0, blank=False)

    def __str__(self):
        return "{}：{} {}".format(self.name, self.func, self.value)


    class Meta:
        verbose_name = "验证器"
        verbose_name_plural = "验证器"



class calculateModel(models.Model):
    class funcChoices(models.TextChoices):
        ADD = 'add', _('加')
        SUB = 'sub', _('减')
        MULT = 'mult', _('乘')
        DIV = "div", _('除')

    name = models.CharField("变量名称", max_length=100, default="variable0",blank=False)
    step = models.ForeignKey("stepModel",unique=False, on_delete=models.CASCADE, auto_created=True)
    value1 = models.CharField("参数1", max_length=100, default="{{variable1}}", blank=False)
    func = models.CharField("计算方法", max_length=5, default=funcChoices.ADD, choices=funcChoices.choices, blank=False)
    value2 = models.CharField("参数2", max_length=100, default="100", blank=False)


    class Meta:
        verbose_name = "计算器"
        verbose_name_plural = "计算器"

    def __str__(self):
        return "{}：{} {} {}".format(self.name, self.value1, self.func, self.value2)


class onStepModel(models.Model):
    class methodTypeChoices(models.TextChoices):
        POST = "POST", _('POST')
        GET = 'GET', _('GET')



    name = models.CharField(stepReplace[stepFiler.interfaceName], max_length=500, default=None, blank=False)
    host = models.CharField(stepReplace[stepFiler.host], max_length=200, default="", blank=False)
    path = models.CharField(stepReplace[stepFiler.path], max_length=200, default="", blank=False)
    method = models.CharField(stepReplace[stepFiler.method], max_length=5, choices=methodTypeChoices.choices,default=methodTypeChoices.POST)  # 步骤方法,应隶属步骤类型
    params = models.JSONField(stepReplace[stepFiler.params], max_length=500, default=None, blank=True)




    class Meta:
        verbose_name = "访问接口详情"
        verbose_name_plural = "访问接口详情"

        ordering = ['name']

    def __str__(self):
        return "{}： {}".format(self.name,self.path)



class stepModel(models.Model):
    class stepTypeChoices(models.TextChoices):
        IF = 'interface', _('接口')
        FUC = 'func', _('方法')
        SQL = "SQL", _('数据库')
        REDIS = "REDIS", _('缓存')

    class interfaceChoices(models.Choices):
        def __init__(self):
            pass

    class Meta:
        verbose_name = "测试步骤"
        verbose_name_plural = "003-接口步骤"

        ordering = ["stepNumber"]


    name = models.CharField(stepReplace[stepFiler.stepFaceName], max_length=500, default=None, blank=False)
    onStep = models.ForeignKey("onStepModel",unique=False, on_delete=models.CASCADE, auto_created=True)

    stepNumber = models.IntegerField("步骤序号",default=10001, auto_created=True)

    created_time = models.DateTimeField(caseReplace[caseFiler.createTime], auto_now=True)  # 创建时间
    updated_time = models.DateTimeField(caseReplace[caseFiler.updateTime], auto_now_add=True)  # 更新时间
    isUse = models.BooleanField(caseReplace[caseFiler.isUse], default=True)


    def __str__(self):
        return "{}-{}".format(self.stepNumber, self.name)




class caseModel(models.Model):
    name = models.CharField(caseReplace[caseFiler.caseName], max_length=500, default=None, blank=False)
    # variable = models.ManyToManyField(variableModel, default=None)
    step = models.ManyToManyField(stepModel, default=None, blank=True)

    created_time = models.DateTimeField(caseReplace[caseFiler.createTime], auto_now=True)  # 创建时间
    updated_time = models.DateTimeField(caseReplace[caseFiler.updateTime], auto_now_add=True)  # 更新时间
    isUse = models.BooleanField(caseReplace[caseFiler.isUse], default=True)

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = "002-测试用例"
        default_related_name = "用例集"

        ordering = ["name"]

    def __str__(self):
        return "{}".format(self.name)


class planModel(models.Model):
    class appTypeTextChoices(models.TextChoices):
        MAIN = 'MN', _('主包')
        STAR = 'SR', _('星辰')

    class environmentTextChoices(models.TextChoices):
        TEST = 'TEST', _('测试')
        DEV = 'DEV', _('开发')
        PRODUCT = "PRO", _('生产')

    name = models.CharField(planReplace[planFiler.planName], max_length=500, default=None, blank=False)
    environment = models.CharField(planReplace[planFiler.environment], max_length=5,
                                   choices=environmentTextChoices.choices, default=environmentTextChoices.TEST)
    app_type = models.CharField(planReplace[planFiler.appType], max_length=5, choices=appTypeTextChoices.choices,
                                default=appTypeTextChoices.MAIN)
    case_list = models.ManyToManyField(caseModel,"用例集", default=None, blank=True)
    # variable = models.ForeignKey("variableModel",on_delete=models.CASCADE,default=None,blank=True)

    created_time = models.DateTimeField(caseReplace[caseFiler.createTime], auto_now=True)  # 创建时间
    updated_time = models.DateTimeField(caseReplace[caseFiler.updateTime], auto_now_add=True)  # 更新时间
    isUse = models.BooleanField(planReplace[planFiler.isUse], default=True)

    class Meta:
        verbose_name = "测试计划"
        verbose_name_plural = "001-测试计划"



    def __str__(self):
        return "{}".format(self.name)

