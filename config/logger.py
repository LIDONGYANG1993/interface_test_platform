import logging
import os
from logging import handlers

DEBUG_LOG = False
project_path = os.path.dirname(os.path.dirname(__file__))

class Logger(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self,
                 filename,
                 level='info',
                 back_count=5,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):


        self.filename = filename
        self.level = level
        self.back_count = back_count
        self.fmt = fmt
        self.logger = self.logger_init()


    def logger_init(self):
        f_dir, f_name = os.path.split(self.filename)
        os.makedirs(f_dir, exist_ok=True)  # 当前目录新建log文件夹
        the_logger = logging.getLogger(self.filename)
        the_logger.handlers.clear()
        format_str = logging.Formatter(self.fmt)  # 设置日志格式
        the_logger.setLevel(self.level_relations.get(self.level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.RotatingFileHandler(filename=self.filename, backupCount=self.back_count,encoding='utf-8')  # 往文件里写入指定间隔时间自动生成文件的Handler
        th.setFormatter(format_str)  # 设置文件里写入的格式
        the_logger.addHandler(sh)  # 把对象加到logger里
        the_logger.addHandler(th)
        the_logger.propagate = False
        return the_logger


# 测试
if __name__ == '__main__':
    logger = Logger('../result/logs/2020/app.log', 'debug', 5).logger
    logger.debug('debug')
    logger.info('info')
    logger.warning('警告')
    logger.error('报错')
    logger.critical('严重')