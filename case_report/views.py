from django.shortcuts import render

# Create your views here.
from django.template import loader

from case_report.core.read_report import *
from django.http import HttpResponse

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
