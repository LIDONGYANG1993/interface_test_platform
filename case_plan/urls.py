from django.contrib import admin
from django.urls import path

from case_plan import views

url_run_debugging = [
    path('planmodel', views.run_plan_by_id, ),  # 跑一整个计划 HTTP://1.116.254.250:8000/run/plan?data_id=1  对应001-测试计划
    path('casemodel', views.run_case_by_id),  # 单跑一条用例 HTTP://1.116.254.250:8000/run/case?data_id=1   对应002-测试用例
    path('stepmodel', views.run_step_by_id),  # 单跑一条用例 HTTP://1.116.254.250:8000/run/step?data_id=1   对应003-测试步骤
    path('update/interface/byCat', views.update_interface_by_cat),
    path('requestinfomodel', views.run_request_by_id),  # 单跑一个接口  HTTP://1.116.254.250:8000/run/requestInfo?data_id=1  # 对应004-接口参数
    path('updatejob', views.update_job),  # 单跑一个接口  HTTP://1.116.254.250:8000/run/requestInfo?data_id=1  # 对应004-接口参数

]


def debug_url():
    name = "case_plan"
    url_case = (url_run_debugging, name, name)
    return url_case
