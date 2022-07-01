#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/05/25
# @Name  : 杨望宇
from pathlib import Path

from case_plan.models import taskModel
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def get_tasks():
    tasks = taskModel.objects.filter(is_used=True)
    res = []
    for task in tasks:
        make = make_task(task)
        res.append((make["time"], make["func"], make["args"],{}, make["logs"]))
    return res

def make_task(task: taskModel):
    time_repeat = "{} {} {} {} {}"
    time_save = default_time()
    if task.self_set:
        res_time = task.self_set
    else:
        if task.expectation_time.hour:
            time_save[0] = task.expectation_time.minute
            time_save[1] = task.expectation_time.hour
        if task.repeat:
            if task.repeat_type == task.repeatTypeChoices.MOON:
                time_save[2] = task.repeat_moon
            if task.repeat_type == task.repeatTypeChoices.WEEKS:
                time_save[4] = task.repeat_week
        else:
            time_save[2] = task.expectation_data.day
            time_save[3] = task.expectation_data.month
        res_time = time_repeat.format(time_save[0], time_save[1], time_save[2], time_save[3], time_save[4])

    result = {
        "time": res_time,
        "func": "case_report.core.runFunc.run_plan_report_ding",
        "args": [task.plan.id, task.is_ding],
        "logs": ">> {}/logs/crontab/{}-{}.log".format(BASE_DIR, task.name, task.plan.name),
    }
    return result


def default_time():
    return ["30", "08", "*", "*", "*"]


if __name__ == '__main__':
    get_tasks()
