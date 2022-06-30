from django.contrib import admin

# Register your models here.

from case_report.models import *
from case_plan.admin import *


@admin.register(planReportModel)
class planReportAdmin(ImportExportModelAdmin):
    pass

@admin.register(caseReportModel)
class caseReportAdmin(ImportExportModelAdmin):
    pass


@admin.register(stepReportModel)
class stepReportAdmin(ImportExportModelAdmin):
    pass


@admin.register(requestInfoReportModel)
class requestReportAdmin(ImportExportModelAdmin):
    pass

@admin.register(assertsReportModel)
class assertsReportAdmin(ImportExportModelAdmin):
    pass


@admin.register(calculaterReportModel)
class calculaterReportAdmin(ImportExportModelAdmin):
    pass

@admin.register(variableReportModel)
class variableReportAdmin(ImportExportModelAdmin):
    pass

@admin.register(extractorReportModel)
class extractorReportAdmin(ImportExportModelAdmin):
    pass


@admin.register(defaultReportModel)
class defaultReportAdmin(ImportExportModelAdmin):
    pass


