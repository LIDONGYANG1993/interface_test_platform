from django.shortcuts import render

# Create your views here.

from case_plan.core.runFunc import *
from config.casePlan import response
from django.http import HttpResponse
from django.http import JsonResponse
from config.wanba.reptileYapi.get_yapi_insert_interface import Interface

def run_case_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update({"data":run_case(data_id)})
    return JsonResponse(result)



def run_request_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update({"data":run_requestInfo(data_id)})
    return JsonResponse(result)

def run_plan_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update({"data":run_plan(data_id)})
    return JsonResponse(result)

def run_step_by_id(request):
    result = response.result
    request: django.http.request.HttpRequest
    data = request.GET
    data_id = data.get("data_id", None)
    if not data_id:
        return JsonResponse(response.params_error)
    result.update({"data":run_step(data_id)})
    return JsonResponse(result)


def update_interface_by_cat(request):
    result = response.result
    request: django.http.request.HttpRequest
    data_get = request.GET
    data_post = request.POST
    cat_id_get = data_get.get("cat_id", None)
    cat_id_post = data_post.get("cat_id", None)
    if not (cat_id_get or cat_id_post):
        return JsonResponse(response.params_error)
    cat_id = cat_id_get if cat_id_get else cat_id_post
    inter = Interface()
    res_get = inter.import_data_by_cat(cat_id)
    if res_get[0]:
        result.update({"data":res_get[1]})
    else:
        return JsonResponse(response.cat_id_error)
    return JsonResponse(result)


def update_job(request):
    result = response.result
    add_job()
    return JsonResponse(result)
