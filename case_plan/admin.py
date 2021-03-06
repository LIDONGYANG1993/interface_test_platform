from django.contrib import admin
from django.db.models import JSONField, URLField
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.admin.widgets import AdminURLFieldWidget
from fieldsets_with_inlines import FieldsetsInlineMixin
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import *
from inline_actions.admin import InlineActionsMixin
from inline_actions.admin import InlineActionsModelAdminMixin
from inline_actions.actions import DefaultActionsMixin

# Register your models here.

# 配置标题
admin.site.site_title = "接口场景化平台"
admin.site.site_header = "接口场景化平台"
admin.site.index_title = "接口场景化平台"


# 公共类型
class publicAdmin(FieldsetsInlineMixin, InlineActionsModelAdminMixin, ImportExportModelAdmin):
    list_display = ["id", 'name', "created_time", "updated_time"]  # 展示字段
    list_display_links = ["id", "name"]  # 展示字段链
    readonly_fields = ["created_time", "updated_time"]  # 只读字段
    search_fields = ["name", "id"]  # 搜索字段
    empty_value_display = '无'  # 默认空值展示字段
    list_select_related = False  # 开启关系型搜索
    list_per_page = 20  # 分页数量
    ordering = ["id", "name"]  # 排序字段

    show_full_result_count = True  # 关闭显示总数

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(height="350px")},
    }

    def save_model(self, request, obj, form, change):  # 自动保存修改和创建人
        if not change:
            obj.create_user = request.user.username
        obj.update_user = request.user.username
        super().save_model(request, obj, form, change)

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


class publicLine(admin.TabularInline):
    extra = 0
    can_delete = False
    template = "change/tabular.html"


class calculateLine(publicLine):
    model = calculaterModel


class extractorLine(publicLine):
    model = extractorModel


class assertLine(publicLine):
    model = assertsModel


class variableLine(publicLine):
    verbose_name_plural = "计划变量"
    model = variableModel


class caseAssertLine(assertLine):
    classes = ["collapse"]


class caseVariableLine(variableLine):
    verbose_name_plural = "用例变量"


class stepLine(InlineActionsMixin, DefaultActionsMixin, publicLine):
    model = stepModel
    exclude = ["params", ]
    sortable_field_name = "stepNumber"
    autocomplete_fields = ["requestInfo", ]


@admin.register(requestInfoModel)
class requestInfoAdmin(publicAdmin):
    change_list_template = "admin/change_list_import.html"
    list_display = ("id", 'name', 'path', 'params', "doc_url",)
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["doc_url", "host", "path"]}),
        ("参数集", {"fields": ["params"]}),
    ]
    search_fields = ["name", "id", "path"]
    ordering = ["name"]


@admin.register(stepModel)
class stepAdmin(publicAdmin):
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('所属用例', {'fields': ["case"]}),
        ('基本信息', {'fields': ["requestInfo", "stepNumber", ]}),
        ('替换参数', {'fields': ["params", ], "classes": []}),
        extractorLine, calculateLine, assertLine
    ]
    inlines = []
    autocomplete_fields = ["case", "requestInfo"]
    list_display = ("id", "stepNumber", "case", "name", "created_time", "updated_time")
    search_fields = ["name", "id", "case__name"]
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(height=150)},
    }


@admin.register(caseModel)
class caseAdmin(publicAdmin):
    list_display = ("id", 'name', "model", "step_str", "create_user", "update_user", "created_time", "updated_time")
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        (None, {'fields': ['model']}),
        caseVariableLine,
        stepLine,
        caseAssertLine,
    ]
    ordering = ["name"]
    search_fields = ["name", "id", "model"]


@admin.register(dingModel)
class dingAdmin(publicAdmin):
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["ding_url", "group"]})
    ]


@admin.register(planModel)
class planAdmin(publicAdmin):
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["default", "case"]}),
        ('机器人', {'fields': ["ding"]}),
        variableLine
    ]

    list_display = (
        "id", 'name', "case_list_str",
        "val_list_str", "create_user",
        "update_user", "default",
        "created_time",
        "updated_time")
    autocomplete_fields = ["case", "ding"]


# @admin.register(assertsModel)
# class assertAdmin(publicAdmin):
#     list_display = ("id", 'name',"func","name_another")
#     fieldsets_with_inlines = [
#         (None, {'fields': ['name']}),
#         (None, {'fields': ["func", "name_another"]})
#     ]
#
#
# @admin.register(extractorModel)
# class extractorAdmin(publicAdmin):
#     list_display = ("id", 'name', 'value', "condition")
#     fieldsets_with_inlines = [
#         (None, {'fields': ['name']}),
#         (None, {'fields': ["value", "condition"]})
#     ]
#
#
# @admin.register(calculaterModel)
# class calculateAdmin(publicAdmin):
#     list_display = ("id", 'name', 'value1', "func", "value2")
#     fieldsets_with_inlines = [
#         (None, {'fields': ['name']}),
#         (None, {'fields': ["value1", "func", "value2"]})
#     ]
#
#
# @admin.register(variableModel)
# class variableAdmin(publicAdmin):
#     list_display = ("id", 'name', 'value')
#     fieldsets_with_inlines = [
#         (None, {'fields': ['name']}),
#         (None, {'fields': ["value"]})
#     ]
#


# @admin.register(defaultModel)
# class defaultAdmin(publicAdmin):
#     fieldsets_with_inlines = [
#         (None, {'fields': ['name']}),
#         (None, {'fields': ["value", ]})
#     ]
#
#
# @admin.register(tokenModel)
# class tokenAdmin(publicAdmin):
#     list_display = ["uid", "token", "environment", "app_type"]
#     list_display_links = ["uid", "token", "environment"]
#     fieldsets_with_inlines = [
#         (None, {'fields': ['uid']}),
#         (None, {'fields': ["token", "environment", "app_type"]})
#     ]


@admin.register(taskModel)
class taskAdmin(publicAdmin):
    change_list_template = "admin/change_list_task.html"
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        (None, {'fields': ['plan']}),
        (None, {'fields': [('is_ding', 'is_used')]}),
        ("执行时间：", {'fields': ["expectation_time"]}),
        ("运行周期：", {'fields': [("is_not_repeat", "expectation_data"), ]}),
        ("每天", {'fields': ["is_evey_day"]}),
        ("每周", {'fields': ["is_evey_week", "repeat_week"]}),
        ("每月", {'fields': ["is_evey_moon", "repeat_moon"]}),

        ("运行周期-自定义", {'fields': ["self_set"], "classes": ["collapse", ]}),
    ]

    def save_model(self, request, obj: taskModel, form, change):
        obj.repeat = not obj.is_not_repeat
        if obj.is_evey_day:
            obj.repeat_type = obj.repeatTypeChoices.DAY
        elif obj.is_evey_week:
            obj.repeat_type = obj.repeatTypeChoices.WEEKS
        elif obj.is_evey_moon:
            obj.repeat_type = obj.repeatTypeChoices.MOON
        else:
            obj.repeat = False
        super().save_model(request, obj, form, change)
