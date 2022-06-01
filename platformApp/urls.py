"""interface_test_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from case_plan import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('run/plan', views.run_plan_by_id),  # 跑一整个计划 HTTP://1.116.254.250:8000/run/plan?data_id=1  对应001-测试计划
    path('run/case', views.run_case_by_id),  # 单跑一条用例 HTTP://1.116.254.250:8000/run/case?data_id=1   对应002-测试用例
    path('run/step', views.run_step_by_id),  # 单跑一条用例 HTTP://1.116.254.250:8000/run/step?data_id=1   对应003-测试步骤
    path('run/requestInfo', views.run_request_by_id),  # 单跑一个接口  HTTP://1.116.254.250:8000/run/requestInfo?data_id=1  # 对应004-接口参数
]
