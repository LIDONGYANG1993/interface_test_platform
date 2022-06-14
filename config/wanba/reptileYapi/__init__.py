
from config.yapi_config import yapi_name, yapi_pwd
import django
django.setup()

# 初始化请求头
header = {
    "Content-Type": "application/json"
}

keys = "620c99dbc94c78a228b3296a"


GROUP = 'yapi_group'
PROJECT = 'yapi_project'
CAT = 'yapi_cat'
INTERFACE = 'yapi_interface'
CASE = 'auto_case'

update_list_project_id = [230, ]
