from django import forms, db
from django.contrib import admin

# Register your models here.
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from fieldsets_with_inlines import FieldsetsInlineMixin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import *



class publicAdmin(FieldsetsInlineMixin, ImportExportModelAdmin):




    list_display = ["id", 'name', "created_time", "updated_time"]  # 展示字段
    list_display_links = ["id", "name"]  # 展示字段链
    readonly_fields = ["created_time", "updated_time"]
    search_fields = ["name", "id"]  # 搜索字段
    empty_value_display = '无'  # 默认空值展示字段
    list_select_related = True
    list_per_page = 50


    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def save_model(self, request, obj:stepModel, form, change):  # 自动保存修改和创建人
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



class stepResources(resources.ModelResource):
    class Meta:
        model = stepModel


class publicLine(admin.TabularInline):
    extra = 0


class calculateLine(publicLine):
    model = calculaterModel


class extractorLine(publicLine):
    model = extractorModel


class assertLine(publicLine):
    model = assertsModel



class variableLine(publicLine):
    model = variableModel


class caseAssertLine(assertLine):
    classes = ["collapse"]



class caseVariableLine(variableLine):
    verbose_name = "用例变量"
    classes = ["collapse"]


class stepLine(publicLine):
    model = stepModel
    sortable_field_name = "stepNumber"


# @admin.register(variable)
# class variableAdmin(publicAdmin):
#     list_display = ("id", 'name', 'value')
#



@admin.register(defaultModel)
class defaultAdmin(publicAdmin):
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        (None, {'fields': ["value",]})
    ]

@admin.register(requestInfoModel)
class requestInfoAdmin(publicAdmin):
    list_display = ("id", 'name', 'path', 'params')
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["host","path","headers"]}),
        ("参数集", {"fields": ["params"]}),
    ]




@admin.register(stepModel)
class stepAdmin(publicAdmin):
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["requestInfo","stepNumber",]}),
        ('替换参数', {'fields': ["params",], "classes":["collapse", ]}),
        extractorLine, calculateLine, assertLine
    ]
    inlines = []
    list_display = ("id","stepNumber", 'name',"create_user", "update_user", "created_time", "updated_time")



    autocomplete_fields = []


@admin.register(caseModel)
class caseAdmin(publicAdmin):
    @staticmethod
    def step_str(obj:caseModel):
        return [rel for rel in obj.step.all()]

    list_display = ("id", 'name', "step_str","create_user","update_user","created_time", "updated_time")
    filter_horizontal = ["step", ]
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        caseVariableLine,
        ('用例步骤列表', {'fields': ["step",]}),
        caseAssertLine,
    ]
    ordering = ["name"]


@admin.register(planModel)
class planAdmin(publicAdmin):

    @staticmethod
    def case_list_str(obj):
        return [rel for rel in obj.case.all().order_by("name")]

    @staticmethod
    def val_list_str(obj):
        return [rel for rel in obj.variable.all().order_by("name")]

    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["environment_and_type","case"]}),
        variableLine
    ]

    list_display = ("id", 'name', "case_list_str", "val_list_str","create_user","update_user","environment_and_type","created_time", "updated_time")
    autocomplete_fields = ["case", ]

@admin.register(tokenModel)
class tokenAdmin(publicAdmin):
    list_display = ["uid","token"]
    list_display_links = ["uid","token"]
    fieldsets_with_inlines = [
        (None, {'fields': ['uid']}),
        (None, {'fields': ["token",]})
    ]


@admin.register(assertsModel)
class assertAdmin(publicAdmin):
    list_display = ("id", 'name',"func","name_another")
    fieldsets_with_inlines = [
        (None, {'fields': ['name']}),
        (None, {'fields': ["func", "name_another"]})
    ]


# @admin.register(extractor)
# class extractorAdmin(publicAdmin):
#     pass
#

# @admin.register(calculater)
# class calculateAdmin(publicAdmin):
#     pass
