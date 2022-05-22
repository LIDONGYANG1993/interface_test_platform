from django.contrib import admin

# Register your models here.

from .models import *


class publicAdmin(admin.ModelAdmin):
    search_fields = ["name", "id"]
    list_display_links = ["id","name"]
    list_display = ["id", 'name']

    list_per_page = 50


class publicLine(admin.TabularInline):
    extra = 0


class calculateLine(publicLine):
    model = calculateModel


class assertLine(publicLine):
    model = assertModel


class responseLine(publicLine):
    model = responseModel


class planLine(publicLine):
    model = variableModel



@admin.register(variableModel)
class variableAdmin(publicAdmin):
    list_display = ("id", 'name', 'value')


@admin.register(onStepModel)
class onStepAdmin(publicAdmin):
    list_display = ("id",'name', 'path', 'params')


@admin.register(stepModel)
class stepAdmin(publicAdmin):

    fieldsets = [
        (None, {'fields': ['name']}),
        ('Date information', {'fields': ["onStep"], 'classes': ['responseModel']}),
    ]
    inlines = [responseLine,calculateLine,assertLine]
    list_display = ("id",'name',)
    autocomplete_fields = []




@admin.register(caseModel)
class caseAdmin(publicAdmin):
    @staticmethod
    def step_str(obj):
        return [rel for rel in obj.step.all()]

    list_display = ("id",'name', "step_str")
    autocomplete_fields = ["step", ]


@admin.register(planModel)
class planAdmin(publicAdmin):

    @staticmethod
    def case_list_str(obj):
        return [rel for rel in obj.name.all()]


    fieldsets = [
        (None, {'fields': ['name']}),
        ('基本信息', {'fields': ["environment", "app_type", "case_list"], 'classes': ['variableModel']}),
    ]
    inlines = [planLine]

    list_display = ("id",'name', "case_list_str")
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


