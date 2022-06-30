#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
import json
from case_report.models import *
import requests
import urllib3


def send_ding(url, title, msg, isAtAll=None, atUser=None, atMobiles=None):
    if not url: return
    json_ = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": msg},
        "at": {"atMobiles": atMobiles, "atUserIds": atUser, "isAtAll": isAtAll}
    }
    urllib3.disable_warnings()
    res = requests.post(url, data=bytes(json.dumps(json_), 'utf-8'), headers={'Content-Type': 'application/json'},
                        verify=False)
    print(res.json())
    return res

def make_report_ding(report:planReportModel):
    title = "场景测试报告"
    msg = '-' * 50 + '\n\n' + "日期：{}\n\n" + "计划名称：{}\n\n" + "计划编号：{}\n\n用例总数：{}\n\n<font color='#0eb95e'>通过：{}</font>\n\n<font color='#df0000'>失败：{}</font>\n\n<font color='#df0000'>异常：{}</font>\n\n失败列表：\n\n"
    msg = msg.format(
        report.created_time,
        report.name,
        report.from_data.id,
        report.pass_count + report.fail_count + report.error_count,
        report.pass_count,
        report.fail_count,
        report.error_count
    )
    case_msg = ""
    for case in report.casereportmodel_set.all():
        case:caseReportModel
        if case.is_pass:
            continue
        _case_msg = '-' * 50 + "\n\n名称：{}\n\n 原因：{}\n\n"
        case_msg = case_msg + _case_msg.format(
            case.name,
            case.msg.split("\n")[-2]
        )
    url = None
    if report.from_data.ding:
        url = report.from_data.ding.ding_url
    return url, title, msg + case_msg

