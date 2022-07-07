#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/07/07
# @Name  : 杨望宇
import csv

import yaml

def read_task(path):
    name = path / "templates/yml/task.yml"
    # name = "../../templates/yml/task.yml"
    res = []
    with open(name, "r", encoding="utf-8", ) as f:
        data = yaml.safe_load(f)
        for task in data:
            res.append((task[0], task[1], task[2], task[3], task[4]))
    return res


if __name__ == '__main__':
    read_task("../../.")
