from django import forms, db
from django.contrib import admin

# Register your models here.
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import *



class publicAdmin(ImportExportModelAdmin):


    list_display = ["id", 'name',]  # 展示字段
    list_display_links = ["id", "name"]  # 展示字段链接
    readonly_fields = ["create_user","update_user", "created_time", "updated_time"]
    search_fields = ["name", "id"]  # 搜索字段
    empty_value_display = '无'  # 默认空值展示字段
    list_select_related = True
    list_per_page = 50

    def save_model(self, request, obj:step, form, change):  # 自动保存修改和创建人
        if not change:
            obj.create_user = request.user
        obj.update_user = request.user
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
        model = step


class publicLine(admin.TabularInline):
    extra = 0
    fk_name = []


class calculateLine(publicLine):
    model = calculater



class assertLine(publicLine):
    model = asserts


class responseLine(publicLine):
    model = response


class responseStacked(admin.StackedInline):
    model = response
    show_change_link = True



class variableLine(publicLine):
    model = variable


class stepLine(publicLine):
    model = step
    sortable_field_name = "stepNumber"


@admin.register(variable)
class variableAdmin(publicAdmin):
    list_display = ("id", 'name', 'value')





@admin.register(onStep)
class onStepAdmin(publicAdmin):
    list_display = ("id", 'name', 'path', 'params')
    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["host","path",]}),
        ("参数集", {"fields": ["params"]}),
    ]
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }




@admin.register(step)
class stepAdmin(publicAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["onStep","stepNumber",]})
    ]
    inlines = [responseLine, calculateLine, assertLine]
    list_display = ("id","stepNumber", 'name',"create_user", "update_user", "created_time", "updated_time")



    autocomplete_fields = []


@admin.register(case)
class caseAdmin(publicAdmin):
    @staticmethod
    def step_str(obj:case):
        return [rel for rel in obj.step.all().order_by("name")]

    list_display = ("id", 'name', "step_str","created_time", "updated_time")
    filter_horizontal = ["step", ]
    fieldsets = [
        (None, {'fields': ['name']}),
        ('用例步骤列表`', {'fields': ["step",]}),
    ]
    ordering = ["name"]


@admin.register(plan)
class planAdmin(publicAdmin):

    @staticmethod
    def case_list_str(obj):
        return [rel for rel in obj.name.all().order_by("name")]

    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["environment", "app_type", "case"]}),
    ]
    inlines = [variableLine]

    list_display = ("id", 'name', "case_list_str", "created_time", "updated_time")
    autocomplete_fields = ["case", ]


@admin.register(asserts)
class assertAdmin(publicAdmin):
    pass


@admin.register(response)
class responseAdmin(publicAdmin):
    pass


@admin.register(calculater)
class calculateAdmin(publicAdmin):
    pass
