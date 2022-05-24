from django.contrib import admin

# Register your models here.

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import fields
from import_export.formats import base_formats
from .models import *


class publicAdmin(ImportExportModelAdmin):

    list_display = ["id", 'name',]  # 展示字段
    list_display_links = ["id", "name"]  # 展示字段链接
    search_fields = ["name", "id"]  # 搜索字段
    list_select_related = True
    # actions = ["add","change"]
    # actions_on_bottom = True
    # search_help_text = "??"
    # autocomplete_fields = ["name"]

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         readonly_fields = ("created_time", "updated_time")  # 可新增不可修改
    #     else:
    #         readonly_fields = ("created_time", )
    #     return readonly_fields

    list_per_page = 50

    def has_add_permission(self, request):
        # 禁用添加按钮
        return True

    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return True

    def get_export_formats(self):  # 该方法是限制格式
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


class stepResources(resources.ModelResource):
    class Meta:
        model = stepModel


class publicLine(admin.TabularInline):
    extra = 0



class calculateLine(publicLine):
    model = calculateModel


class assertLine(publicLine):
    model = assertModel


class responseLine(publicLine):
    model = responseModel


class responseStacked(admin.StackedInline):
    model = responseModel
    show_change_link = True


    # classes = ["collapse"]


class variableLine(publicLine):
    model = variableModel


class stepLine(publicLine):
    model = stepModel


@admin.register(variableModel)
class variableAdmin(publicAdmin):
    list_display = ("id", 'name', 'value')


@admin.register(onStepModel)
class onStepAdmin(publicAdmin):
    list_display = ("id", 'name', 'path', 'params')


@admin.register(stepModel)
class stepAdmin(publicAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["onStep","stepNumber",], 'classes': ['toggle']}),
    ]
    inlines = [responseStacked, calculateLine, assertLine]
    list_display = ("id","stepNumber", 'name', "created_time", "updated_time")
    autocomplete_fields = []


@admin.register(caseModel)
class caseAdmin(publicAdmin):
    @staticmethod
    def step_str(obj:caseModel):
        return [rel for rel in obj.step.all().order_by("name")]

    autocomplete_fields = ["step"]
    # inlines = [stepLine]
    list_display = ("id", 'name', "step_str","created_time", "updated_time")
    filter_horizontal = ["step", ]
    ordering = ["name"]


@admin.register(planModel)
class planAdmin(publicAdmin):

    @staticmethod
    def case_list_str(obj):
        return [rel for rel in obj.name.all().order_by("name")]

    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["environment", "app_type", "case_list"], 'classes': ['collapse']}),
    ]
    inlines = [variableLine]

    list_display = ("id", 'name', "case_list_str", "created_time", "updated_time")
    autocomplete_fields = ["case_list", ]


@admin.register(assertModel)
class assertAdmin(publicAdmin):
    pass


@admin.register(responseModel)
class responseAdmin(publicAdmin):
    pass


@admin.register(calculateModel)
class calculateAdmin(publicAdmin):
    pass
