from django.shortcuts import render

# Create your views here.

from case_plan.core.runFunc import *
from config.casePlan import response
from django.http import HttpResponse
from django.http import JsonResponse

def run_case_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update(run_case(data_id))
    return JsonResponse(result)



def run_request_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update(run_requestInfo(data_id))
    return JsonResponse(result)

def run_plan_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update(run_plan(data_id))
    return JsonResponse(result)

def run_step_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update(run_step(data_id))
    return JsonResponse(result)
