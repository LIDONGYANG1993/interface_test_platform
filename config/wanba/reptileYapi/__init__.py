
from config.yapi_config import yapi_name, yapi_pwd
import django
django.setup()

# 初始化请求头
header = {
    "Content-Type": "application/json"
}

keys = "620c99dbc94c78a228b3296a"

import os

######################## 路径配置 #####################

project_path = os.path.dirname(os.path.dirname(__file__))

yaml_path = os.path.join(project_path, 'case_data')
mongoDB =  {
    "mongoHost": "t1.kuaishebao.com",
    "mongoDB": "interface_platform_db",
    "mongoUser": None,
    "mongoPwd": None
}


# 线上环境
online_config = {
    "mongoHost": "mongodb://dds-2ze4d40d09c596541731-pub.mongodb.rds.aliyuncs.com:3717",
    # "mongoHost": "mongodb://dds-2ze4d40d09c596541.mongodb.rds.aliyuncs.com:3717", # 服务器内部调用
    "mongoDB": "test_platform_db",
    "mongoUser": "root",
    "mongoPwd": "Duuo0xjmwq7s0DHq"
}
#
# mongoDB = {
#     "mongoHost": "localhost",
#     "mongoDB": "test_platform_db",
#     "mongoUser": None,
#     "mongoPwd": None
# }

GROUP = 'yapi_group'
PROJECT = 'yapi_project'
CAT = 'yapi_cat'
INTERFACE = 'yapi_interface'
CASE = 'auto_case'


update_list_project_id = [230, ]
yapi_user = 'yangwangyu'
yapi_pwd = 'Yang840251'