from case_report.core.func import *

from case_plan.core.runFunc import run_plan_and_report


def run_plan_report_ding(data_id, ding: bool = False):
    report = run_plan_and_report(data_id)
    if ding:
        report_msg = make_report_ding(report.model_data)
        send_ding(report_msg[0], report_msg[1], report_msg[2])
