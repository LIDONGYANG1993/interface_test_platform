from django.db import models

# Create your models here.


from case_plan.models import *


class publicReportModel(publicModel):
    is_pass = models.BooleanField(verbose_name=planReplace[planFiler.is_pass], default=False, editable=True, blank=True)
    msg = models.TextField(verbose_name=planReplace[planFiler.msg], default=None, editable=True, blank=True, null=True)

    class Meta:
        abstract = True


class planReportModel(publicReportModel):
    from_data = models.ForeignKey(planModel, verbose_name="源计划", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(planReplace[planFiler.name], max_length=100, default=None, blank=True)
    default = models.OneToOneField("defaultReportModel", on_delete=models.CASCADE, null=True, verbose_name=planReplace[planFiler.environment], max_length=5, default=1)
    pass_count = models.IntegerField(verbose_name="通过", blank=False, default=0)
    fail_count = models.IntegerField(verbose_name="失败", blank=False, default=0)
    error_count = models.IntegerField(verbose_name="异常", blank=False, default=0)


class caseReportModel(publicReportModel):
    from_data = models.ForeignKey(caseModel, verbose_name="源用例", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(caseReplace[caseFiler.name], max_length=100, default=None, blank=True)
    model = models.CharField(caseReplace[caseFiler.model], max_length=100, default=None, blank=True)
    plan = models.ForeignKey("planReportModel", on_delete=models.CASCADE, null=True,verbose_name=caseReplace[caseFiler.plan])


class stepReportModel(publicReportModel):
    from_data = models.ForeignKey(stepModel, verbose_name="源步骤", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(stepReplace[stepFiler.name], max_length=100, default=None, blank=True)
    requestInfo = models.OneToOneField("requestInfoReportModel", verbose_name=stepReplace[stepFiler.requestInfo], unique=False,on_delete=models.CASCADE)
    params = models.JSONField(stepReplace[stepFiler.reParams], default=dict, blank=True)
    stepNumber = models.IntegerField(stepReplace[stepFiler.stepNumber], default=1, auto_created=True)
    case = models.ForeignKey("caseReportModel", verbose_name=stepReplace[stepFiler.case], related_name="step", default=None,blank=True, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)

class requestInfoReportModel(publicReportModel):
    from_data = models.ForeignKey(requestInfoModel, verbose_name="源接口信息", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(requestInfoReplace[requestInfoFiler.name], max_length=100, default=None, blank=True)
    doc_url = models.URLField(requestInfoReplace[requestInfoFiler.doc_url], max_length=255, default="", blank=True)
    host = models.URLField(requestInfoReplace[requestInfoFiler.host], max_length=200, default="", blank=True)
    path = models.CharField(requestInfoReplace[requestInfoFiler.path], max_length=200, default="", blank=True)
    method = models.CharField(requestInfoReplace[requestInfoFiler.method], max_length=5, choices=publicModel.methodTypeChoices.choices, default=publicModel.methodTypeChoices.POST)  # 步骤方法,应隶属步骤类型
    headers = models.JSONField(requestInfoReplace[requestInfoFiler.headers], default=dict, blank=True)
    params = models.JSONField(requestInfoReplace[requestInfoFiler.params], default=dict, blank=True)
    response = models.JSONField(requestInfoReplace[requestInfoFiler.response], default=dict, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)




class variableReportModel(publicModel):
    from_data = models.ForeignKey(variableModel, verbose_name="源变量", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(variableReplace[variableFiler.name], max_length=255, default=None, blank=True)  # 变量名称
    plan = models.ForeignKey("planReportModel", verbose_name=variableReplace[variableFiler.plan], on_delete=models.CASCADE,
                             default=None, blank=True, null=True, editable=False, related_name="variable")
    case = models.ForeignKey("caseReportModel", verbose_name=variableReplace[variableFiler.case], on_delete=models.CASCADE,
                             default=None, blank=True, null=True, editable=False, related_name="variable_case")
    value = models.CharField(variableReplace[variableFiler.value], max_length=255, default="", blank=True)  # 变量初始值

    def __str__(self):
        return "{}：{}".format(self.name, self.value)


class extractorReportModel(publicModel):
    from_data = models.ForeignKey(extractorModel, verbose_name="源提取器", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    step = models.ForeignKey("stepReportModel", verbose_name=extractorReplace[extractorFiler.step], unique=False,
                             on_delete=models.SET_NULL, blank=True, editable=False, null=True)
    name = models.CharField(extractorReplace[extractorFiler.name], max_length=20, default="CODE", blank=True)
    value = models.CharField(extractorReplace[extractorFiler.value], max_length=255, default="code", blank=True)
    condition = models.CharField(extractorReplace[extractorFiler.condition], max_length=50, default="", blank=True)
    result = models.CharField(max_length=255, default="", blank=True)

class assertsReportModel(publicReportModel):
    from_data = models.ForeignKey(assertsModel, verbose_name="源验证器", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(assertsReplace[assertsFiler.value1], max_length=20, default="{{CODE}}", blank=True)

    step = models.ForeignKey("stepReportModel", verbose_name=extractorReplace[extractorFiler.step], unique=False,
                             on_delete=models.CASCADE, blank=True, editable=False, null=True)
    case = models.ForeignKey("caseReportModel", verbose_name=assertsReplace[assertsFiler.case], unique=False,
                             on_delete=models.CASCADE, blank=True, editable=False, null=True)
    func = models.CharField(assertsReplace[assertsFiler.assertMethod], max_length=5,
                            default=publicModel.funcChoices.EQL, choices=publicModel.funcChoices.choices, blank=True)
    name_another = models.CharField(assertsReplace[assertsFiler.value2], max_length=20, default=0, blank=True)
    result = models.CharField(max_length=100, default="", blank=True)

    def __str__(self):
        return "{} {} {}".format(self.name, self.func, self.name_another)



class calculaterReportModel(publicModel):
    from_data = models.ForeignKey(calculaterModel, verbose_name="源计算器", default=None, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(calculatorReplace[calculatorFiler.name], max_length=20, default="variable0", blank=True)
    step = models.ForeignKey("stepReportModel", verbose_name=calculatorReplace[calculatorFiler.step], unique=False,on_delete=models.CASCADE, blank=True, null=True)
    value1 = models.CharField(calculatorReplace[calculatorFiler.Variable1], max_length=20, default="{{variable1}}",blank=True)
    func = models.CharField(calculatorReplace[calculatorFiler.calFunction], max_length=10,default=publicModel.calChoices.ADD, choices=publicModel.calChoices.choices, blank=True)
    value2 = models.CharField(calculatorReplace[calculatorFiler.Variable2], max_length=20, default=100, blank=True)
    result = models.CharField(max_length=100,default="", blank=True)


    def __str__(self):
        return "{}：{} {} {}".format(self.name, self.value1, self.func, self.value2)
