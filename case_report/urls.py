from django.contrib import admin
from django.urls import path

from case_report import views

url_run_debugging = [
    path('view', views.get_report, ),
    path('run', views.run_and_report, ),

]


def debug_url():
    name = "case_report"
    url_case = (url_run_debugging, name, name)
    return url_case
