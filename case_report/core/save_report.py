#!../venv/bin/python3
# -*- coding: utf-8 -*-
# @Date  : 2022/06/24
# @Name  : 杨望宇


from case_report.core import *
from case_plan.core.read_class import *
from case_plan.core.exec_class import *
from case_report.models import *


class publicReport:
    def __init__(self, data_class, report_model):
        self.data_class = data_class
        self.reportModel = report_model

        self.data = None
        self.done = None
        self.report: Model = None

    def create_report(self):
        self.new_report()
        self.make_data()
        self.save_report()

    def new_report(self):
        self.reportModel: models.Model
        self.report = self.reportModel.objects.model(from_data=self.data.model_data)

    def save_report(self):
        self.report.save()

    def get_done_by_done(self, done):
        self.done = done

    def get_data(self, done):
        done: publicDone
        self.get_done_by_done(done)
        self.get_data_by_data(done.get_data)

    def get_data_by_data(self, data):
        self.data = data

    def get_data_by_model(self, model):
        self.data: publicData
        data = self.data_class()
        self.data = data.get_model(model)

    def make_data(self):
        pass

    @staticmethod
    def make_msg(msg_list):
        res_msg = ''
        if not msg_list:
            return res_msg
        for msg in msg_list:
            if msg is msg_list[-1]:
                res_msg = res_msg + msg
                break
            res_msg = res_msg + msg + "\n"
        return res_msg

    @staticmethod
    def exc_filed():
        return ['id', 'created_time', 'updated_time', 'create_user', 'update_user', ]

    @staticmethod
    def make_one_to_one(son_report_class, value):
        report: publicReport
        report = son_report_class()
        report.get_data(value)
        report.create_report()
        return report.report


# 默认数据
class planReport(publicReport):
    report: planReportModel
    data: planData
    done: planDone

    def __init__(self):
        super().__init__(planData, planReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.default = self.make_one_to_one(defaultReport, self.done.default)
        self.report.save()
        self.make_case()
        self.make_variable()
        self.make_result()

    def make_result(self):
        self.done: planDone
        self.done.result_massage()
        self.report.pass_count = self.done.get_pass_count()
        self.report.fail_count = self.done.get_fail_count()
        self.report.error_count = self.done.get_error_count()
        self.report.msg = self.make_msg(self.done.msg)

    def make_case(self):

        self.done: planDone
        for case in self.done.case_list:
            report = caseReport()
            report.get_data(case)
            report.create_report()
            report.make_plan(self.report)

            report.save_report()

    def make_variable(self):
        for variable in self.done.variable:
            report = variableReport()
            report.get_data(variable)
            report.create_report()
            report.make_plan(self.report)
            report.save_report()


class variableReport(publicReport):
    report: variableReportModel
    data: variableData

    def __init__(self):
        super().__init__(variableData, variableReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.value = self.data.model_data.value

    def make_plan(self, report_plan):
        if report_plan:
            self.report.plan = report_plan

    def make_case(self, report_case):
        if report_case:
            self.report.case = report_case


class defaultReport(publicReport):
    report: defaultReportModel
    data: defaultData

    def __init__(self):
        super().__init__(defaultData, defaultReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.value = self.data.model_data.value


class extractorReport(publicReport):
    report: extractorReportModel
    data: extractorData
    done: extractorDone

    def __init__(self):
        super().__init__(extractorData, extractorReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.value = self.data.model_data.value
        self.report.condition = self.data.model_data.condition
        self.report.result = self.done.value

    def make_step(self, report_step):
        self.report.step = report_step

    def make_result(self):
        pass


class calculaterReport(publicReport):
    report: calculaterReportModel
    data: calculaterData
    done: calculaterDone

    def __init__(self):
        super().__init__(calculaterData, calculaterReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.value1 = self.data.model_data.value1
        self.report.func = self.data.model_data.func
        self.report.value2 = self.data.model_data.value2
        self.report.result = self.done.result

    def make_step(self, report_step):
        self.report.step = report_step

    def make_result(self):
        pass


class assertsReport(publicReport):
    report: assertsReportModel
    data: assertData
    done: assertsDone

    def __init__(self):
        super().__init__(assertData, assertsReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.func = self.data.model_data.func
        self.report.name_another = self.data.model_data.name_another
        self.report.is_pass = not self.done.fail if self.done.fail is not None else False
        self.report.msg = self.done.get_msg

    def make_step(self, report_step):
        self.report.step = report_step

    def make_case(self, report_case):
        self.report.case = report_case

    def make_result(self):
        pass


class requestInfoReport(publicReport):
    report: requestInfoReportModel
    data: requestInfoData
    done: requestDone

    def __init__(self):
        super().__init__(requestInfoData, requestInfoReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.doc_url = self.data.model_data.doc_url
        self.report.host = self.data.model_data.host
        self.report.path = self.data.model_data.path
        self.report.method = self.data.model_data.method
        self.report.headers = self.data.model_data.headers
        self.report.params = self.data.model_data.params
        self.report.response = self.done.response_json
        self.report.is_pass = not self.done.error
        self.report.msg = self.make_msg(self.done.msg)
        self.report.status = self.done.status

    def make_response(self):
        pass


class stepReport(publicReport):
    report: stepReportModel
    data: stepData
    done: stepDone

    def __init__(self):
        super().__init__(stepData, stepReportModel)

    def make_data(self):
        self.report.name = self.data.model_data.name
        self.report.params = self.data.model_data.params
        self.report.stepNumber = self.data.model_data.stepNumber
        self.report.requestInfo = self.make_one_to_one(requestInfoReport, self.done.requestInfo)
        self.save_report()
        self.make_calculater()
        self.make_asserts()
        self.make_extractor()
        self.report.is_pass = not self.done.fail
        self.report.msg = self.make_msg(self.done.msg)
        self.report.status = self.done.status

    def make_case(self, report_case):
        self.report.case = report_case

    def make_calculater(self):
        for calculater in self.done.calculator_list:
            report = calculaterReport()
            report.get_data(calculater)
            report.create_report()
            report.make_step(self.report)
            report.save_report()

    def make_asserts(self):
        for asserts in self.done.asserts_list:
            report = assertsReport()
            report.get_data(asserts)
            report.create_report()
            report.make_step(self.report)
            report.save_report()

    def make_extractor(self):
        for extractor in self.done.extractor_list:
            report = extractorReport()
            report.get_data(extractor)
            report.create_report()
            report.make_step(self.report)
            report.save_report()


class caseReport(publicReport):
    report: caseReportModel
    data: caseData
    done: caseDone

    def __init__(self):
        super().__init__(caseData, caseReportModel)

    def make_data(self, parent=None):
        self.report.model = self.data.model_data.model
        self.report.name = self.data.model_data.name
        self.save_report()
        self.make_variable()
        self.make_step()
        self.make_asserts()
        self.report.is_pass = not self.done.fail
        self.report.msg = self.make_msg(self.done.msg)

    def make_plan(self, report_plan):
        self.report.plan = report_plan

    def make_variable(self):
        for variable in self.done.variable:
            report = variableReport()
            report.get_data(variable)
            report.create_report()
            report.make_case(self.report)
            report.save_report()

    def make_step(self):
        for step in self.done.step_list:
            report = stepReport()
            report.get_data(step)
            report.create_report()
            report.make_case(self.report)
            report.save_report()

    def make_asserts(self):
        for asserts in self.done.asserts_list:
            report = assertsReport()
            report.get_data(asserts)
            report.create_report()
            report.make_case(self.report)
            report.save_report()


if __name__ == '__main__':
    case_THE = caseReport()
    pass
