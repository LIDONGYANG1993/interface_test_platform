import threading

from django.shortcuts import render

# Create your views here.
from django.template import loader

from case_report.core.read_report import *
from django.http import HttpResponse
from django.http import JsonResponse

from case_report.core.runFunc import run_plan_report_ding
from config.casePlan import response


def get_report(request):
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    report = planReportData(dataId=data_id)
    template = loader.get_template('report/report.html')

    context = {
        'report': report.data_dict,
    }
    return HttpResponse(template.render(context, request))


def run_and_report(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    ding = data.get("ding", None)
    if not data_id:
        return JsonResponse(response.params_error)
    if ding == "1": ding = True
    else:ding = False
    threading.Thread(target=run_plan_report_ding, args=[data_id,ding]).start()
    return JsonResponse(result)
