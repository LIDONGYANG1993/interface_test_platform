from django.shortcuts import render

# Create your views here.
from django.template import loader

from case_report.core.read_report import *
from django.http import HttpResponse
from case_report.core.func import *

def get_report(request):
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    ding = data.get("ding", None)
    report = planReportData(dataId=data_id)
    template = loader.get_template('report/report.html')


    if ding == "1":
        report_msg = make_report_ding(report.model_data)
        send_ding(report_msg[0], report_msg[1],report_msg[2])
    context = {
        'report': report.data_dict,
    }
    return HttpResponse(template.render(context, request))
