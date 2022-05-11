import datetime
import time

from django.db import models
import mongoengine
from django.utils.translation import gettext_lazy as _

# Create your models here.


class planMongoengine(models.Model):
    class appTypeTextChoices(models.TextChoices):
        MAIN = 'MN', _('主包')
        STAR = 'SR', _('星辰')

    class environmentTextChoices(models.TextChoices):
        TEST = 'TEST', _('测试')
        DEV = 'DEV', _('开发')
        PRODUCT = "PRO", _('生产')

    plan_id = mongoengine.SequenceField(primary_key=True)  # 自动产生一个数列、 递增的
    name = models.CharField(max_length=200,default="测试计划_001",blank=False)
    environment = models.CharField(max_length=5, choices=environmentTextChoices.choices, default=environmentTextChoices.TEST)
    app_type = models.CharField(max_length=5, choices=appTypeTextChoices.choices, default=appTypeTextChoices.MAIN)
    globalVariable = mongoengine.ListField(max_length=1200, default=[])
    caseList = mongoengine.ListField(max_length=1200, default=[])
    isUse = models.BooleanField(default=True)
    # created_time = models.DateTimeField()  # 创建时间
    # updated_time = models.DateTimeField()  # 更新时间


