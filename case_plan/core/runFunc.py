#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import subprocess

from config.casePlan.yamlFilersZh import *
import os
from case_plan.core.exec_class import *
from case_plan.core.read_class import *
from case_plan.core.tasks import BASE_DIR




#  执行单接口
def run_requestInfo(data_id):
    data = requestInfoData(dataId=data_id)
    done = requestDone(data.data_dict)
    done.request()
    done.asserts()
    done.assert_wanba()
    return done.result_for_api()


#  执行单个步骤
def run_step(data_id):
    data = stepData(dataId=data_id)
    done = stepDone(data.data_dict)
    done.run_in_step()
    return done.result_for_api()


#  执行单条用例
def run_case(data_id):
    data = caseData(dataId=data_id)
    done = caseDone(data.data_dict)
    done.run_in_case()
    return done.result_for_api()

#  执行一整个计划
def run_plan(data_id):
    data = planData(dataId=data_id)
    done = planDone(data.data_dict)
    done.run_in_plan()
    return done.result_for_api()


def run_plan_and_report(data_id):
    from case_report.core.save_report import planReport
    from case_report.core.read_report import planReportData
    data = planData(dataId=data_id)
    done = planDone(data.data_dict)
    report = planReport()
    done.run_in_plan()
    report.get_data_by_data(data)
    report.get_done_by_done(done)
    report.create_report()
    reportData = planReportData()
    reportData.get_model(report.report)
    return reportData

def add_job():
    print("start——add")
    subprocess.Popen("/bin/sh {}/add_job.sh".format(BASE_DIR))
    print("end——add")



if __name__ == '__main__':
    add_job()