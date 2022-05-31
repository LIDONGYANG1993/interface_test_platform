#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json

from config.casePlan.yamlFilersZh import *
from case_plan.core.classes import *
from case_plan.core.data import *

def run_requestInfo(data_id):
    data = requestInfoData(dataId=data_id)
    done = requestDone(data.data_dict)
    done.request()
    done.asserts()
    done.assert_wanba()
    return done.result_for_api()


def run_step(data_id):
    data = stepData(dataId=data_id)
    done = stepDone(data.data_dict)
    done.run_in_step()
    return done.result_for_api()


def run_case(data_id):
    data = caseData(dataId=data_id)
    done = caseDone(data.data_dict)
    done.run_in_case()
    return done.result_for_api()


def run_plan(data_id):
    data = planData(dataId=data_id)
    done = planDone(data.data_dict)
    done.run_in_plan()
    return done.result_for_api()


if __name__ == '__main__':
    res = run_requestInfo(1)
    print(json.dumps(res))
