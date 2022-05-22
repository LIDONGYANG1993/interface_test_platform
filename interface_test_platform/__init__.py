import sys
import importlib
import pymysql
pymysql.install_as_MySQLdb()


importlib.reload(sys)