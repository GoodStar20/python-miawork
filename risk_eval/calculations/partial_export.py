from risk_eval import models
#from excel import Export, Upload #, create_logger
from excel.export import states
import logging

from excel.data_validation import DataValidator, state_name_to_abbreviation
from random import randint
from django.conf import settings # needed to get BASE_DIR
import shutil
import json

import xlwings as xl
import pythoncom
import os


BASE_DIR = settings.BASE_DIR

def create_logger(pk, wb_type):
    """
    pk: primary key of header
    wb_type: risk_eval or schedule_rating
    """
    # logging parameters #
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler_fname = os.path.join(BASE_DIR, "tmp/export-{}-{}.log".format(wb_type, pk))
    file_handler = logging.FileHandler(file_handler_fname, mode = 'w')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger


bh_format = {
    "account history" :{
        "1": {"policy_period": "A23", "effective_date": "B23", "expiration_date": "C23", "written_premium": "D23", "incurred_losses": "E23",
            "paid_losses": "F23", "total_claims": "G23", "total_indemnity_claims": "H23", "indemnity_claims": "I23", "open_claims": "J23", "actual_loss_ratio": "K23"},
        "2": {"policy_period": "A24", "effective_date": "B24", "expiration_date": "C24", "written_premium": "D24", "incurred_losses": "E24",
            "paid_losses": "F24", "total_claims": "G24", "total_indemnity_claims": "H24", "indemnity_claims": "I24", "open_claims": "J24", "actual_loss_ratio": "K24"},
        "3":{"policy_period": "A25", "effective_date": "B25", "expiration_date": "C25", "written_premium": "D25", "incurred_losses": "E25",
            "paid_losses": "F25", "total_claims": "G25", "total_indemnity_claims": "H25", "indemnity_claims": "I25", "open_claims": "J25", "actual_loss_ratio": "K25"},
        "4":{"policy_period": "A26", "effective_date": "B26", "expiration_date": "C26", "written_premium": "D26", "incurred_losses": "E26",
            "paid_losses": "F26", "total_claims": "G26", "total_indemnity_claims": "H26", "indemnity_claims": "I26", "open_claims": "J26", "actual_loss_ratio": "K26"},
        "5":{"policy_period": "A27", "effective_date": "B27", "expiration_date": "C27", "written_premium": "D27", "incurred_losses": "E27",
            "paid_losses": "F27", "total_claims": "G27", "total_indemnity_claims": "H27", "indemnity_claims": "I27", "open_claims": "J27", "actual_loss_ratio": "K27"},
        "totals": {"written_premium": "D28", "incurred_losses": "E28",
            "paid_losses": "F28", "total_claims": "G28", "total_indemnity_claims": "H28", "indemnity_claims": "I28", "open_claims": "J28", "actual_loss_ratio": "K28"},
        "average all years": {"written_premium": "D29", "incurred_losses": "E29",
            "paid_losses": "F29", "total_claims": "G29", "total_indemnity_claims": "H29", "indemnity_claims": "I29", "open_claims": "J29", "actual_loss_ratio": "K29"}
        },
    "loss rating": {
        "1": {"policy_period": "A32", "valuation_date": "B32", "age": "C32", "industry_ldf": "D32", "trended_payroll": "E32", "ultimate_reported_claims": "F32", "ultimate_indemnity_claims": "G32",  "payroll": "H32", "prior_carrier": "I32", "bh_developed_loss_ratio": "J32", "ult_clm_ratio": "K32"},
        "2": {"policy_period": "A33", "valuation_date": "B33", "age": "C33", "industry_ldf": "D33", "trended_payroll": "E33", "ultimate_reported_claims": "F33", "ultimate_indemnity_claims": "G33",  "payroll": "H33", "prior_carrier": "I33", "bh_developed_loss_ratio": "J33", "ult_clm_ratio": "K33"},
        "3": {"policy_period": "A34", "valuation_date": "B34", "age": "C34", "industry_ldf": "D34", "trended_payroll": "E34", "ultimate_reported_claims": "F34", "ultimate_indemnity_claims": "G34",  "payroll": "H34", "prior_carrier": "I34", "bh_developed_loss_ratio": "J34", "ult_clm_ratio": "K34"},
        "4": {"policy_period": "A35", "valuation_date": "B35", "age": "C35", "industry_ldf": "D35", "trended_payroll": "E35", "ultimate_reported_claims": "F35", "ultimate_indemnity_claims": "G35",  "payroll": "H35", "prior_carrier": "I35", "bh_developed_loss_ratio": "J35", "ult_clm_ratio": "K35"},
        "5": {"policy_period": "A36", "valuation_date": "B36", "age": "C36", "industry_ldf": "D36", "trended_payroll": "E36", "ultimate_reported_claims": "F36", "ultimate_indemnity_claims": "G36",  "payroll": "H36", "prior_carrier": "I36", "bh_developed_loss_ratio": "J36", "ult_clm_ratio": "K36"},
        "totals": {"trended_payroll": "E37", "ultimate_reported_claims": "F37", "ultimate_indemnity_claims": "G37",  "payroll": "H37",  "bh_developed_loss_ratio": "J37", "ult_clm_ratio": "K37"},
        "analysis": {"trended_payroll": "E38", "ultimate_reported_claims": "F38", "ultimate_indemnity_claims": "G38",  "payroll": "H38", "ult_clm_ratio": "K38"},
        "minimum_premium" : {"minimum_premium": "D42"},
        "frequency_rating": {"frequency_rating": "K39"},
        },
    "exmod": {
        "1": {"loss_rate":"K55"},
        "2": {"loss_rate":"K56"},
        "3": {"loss_rate":"K57"},
        "4": {"loss_rate":"K58"},
        "5": {"loss_rate":"K59"}
    }
}

qbe_format = {
    "account history" :{
        "1": {"policy_period": "A16", "effective_date": "B16", "expiration_date": "C16", "written_premium": "D16", "incurred_losses": "E16",
            "paid_losses": "F16", "total_claims": "G16", "total_indemnity_claims": "H16", "indemnity_claims": "I16", "open_claims": "J16", "actual_loss_ratio": "K16"},
        "2": {"policy_period": "A17", "effective_date": "B17", "expiration_date": "C17", "written_premium": "D17", "incurred_losses": "E17",
            "paid_losses": "F17", "total_claims": "G17", "total_indemnity_claims": "H17", "indemnity_claims": "I17", "open_claims": "J17", "actual_loss_ratio": "K17"},
        "3":{"policy_period": "A18", "effective_date": "B18", "expiration_date": "C18", "written_premium": "D18", "incurred_losses": "E18",
            "paid_losses": "F18", "total_claims": "G18", "total_indemnity_claims": "H18", "indemnity_claims": "I18", "open_claims": "J18", "actual_loss_ratio": "K18"},
        "4":{"policy_period": "A19", "effective_date": "B19", "expiration_date": "C19", "written_premium": "D19", "incurred_losses": "E19",
            "paid_losses": "F19", "total_claims": "G19", "total_indemnity_claims": "H19", "indemnity_claims": "I19", "open_claims": "J19", "actual_loss_ratio": "K19"},
        "5":{"policy_period": "A20", "effective_date": "B20", "expiration_date": "C20", "written_premium": "D20", "incurred_losses": "E20",
            "paid_losses": "F20", "total_claims": "G20", "total_indemnity_claims": "H20", "indemnity_claims": "I20", "open_claims": "J20", "actual_loss_ratio": "K20"},
        "totals":{"written_premium": "D21", "incurred_losses": "E21",
            "paid_losses": "F21", "total_claims": "G21", "total_indemnity_claims": "H21", "indemnity_claims": "I21", "open_claims": "J21", "actual_loss_ratio": "K21"},
        "average all years":{"policy_period": "A22", "effective_date": "B22", "expiration_date": "C22", "written_premium": "D22", "incurred_losses": "E22",
            "paid_losses": "F22", "total_claims": "G22", "total_indemnity_claims": "H22", "indemnity_claims": "I22", "open_claims": "J22", "actual_loss_ratio": "K22"}
        },
    "loss rating": {
        "1": {"policy_period": "A26", "valuation_date": "B26", "age": "C26", "developed_losses": "D26", "bf_losses": "E26",
            "selected_ult_losses": "F26", "loss_trend_factor": "G26", "ult_trended_losses": "H26", "payroll": "I26",
            "prior_carrier": "J26", "qbe_developed_loss_ratio": "K26"},
        "2": {"policy_period": "A27", "valuation_date": "B27", "age": "C27", "developed_losses": "D27", "bf_losses": "E27",
            "selected_ult_losses": "F27", "loss_trend_factor": "G27", "ult_trended_losses": "H27", "payroll": "I27",
            "prior_carrier": "J27", "qbe_developed_loss_ratio": "K27"},
        "3": {"policy_period": "A28", "valuation_date": "B28", "age": "C28", "developed_losses": "D28", "bf_losses": "E28",
            "selected_ult_losses": "F28", "loss_trend_factor": "G28", "ult_trended_losses": "H28", "payroll": "I28",
            "prior_carrier": "J28", "qbe_developed_loss_ratio": "K28"},
        "4": {"policy_period": "A29", "valuation_date": "B29", "age": "C29", "developed_losses": "D29", "bf_losses": "E29",
            "selected_ult_losses": "F29", "loss_trend_factor": "G29", "ult_trended_losses": "H29", "payroll": "I29",
            "prior_carrier": "J29", "qbe_developed_loss_ratio": "K29"},
        "5": {"policy_period": "A30", "valuation_date": "B30", "age": "C30", "developed_losses": "D30", "bf_losses": "E30",
            "selected_ult_losses": "F30", "loss_trend_factor": "G30", "ult_trended_losses": "H30", "payroll": "I30",
            "prior_carrier": "J30", "qbe_developed_loss_ratio": "K30"},
        "totals": {"developed_losses": "D31", "ult_trended_losses": "H31", "payroll": "I31", "qbe_developed_loss_ratio": "K31"},
        "avg_all_years": {"ult_trended_losses": "H32", "payroll": "I32",  "prior_carrier": "J30", "qbe_developed_loss_ratio": "K32"},
        "avg_3_years": {"developed_losses": "D33", "ult_trended_losses": "H33", "qbe_developed_loss_ratio": "K33"},
        "minimum_premium": {"minimum_premium": "D35"}
        },
    "exmod": {
        "1": {"loss_rate":"K47"},
        "2": {"loss_rate":"K48"},
        "3": {"loss_rate":"K49"},
        "4": {"loss_rate":"K50"},
        "5": {"loss_rate":"K51"}
    }
}

class ReadCalculations:
    def __init__(self, user_id, pk, carrier = 'BH',):
        self.user_id = user_id
        self.pk = pk
        self.carrier = carrier

        if carrier == "BH":
            fname = os.path.join(BASE_DIR, "excel/json/export/bh_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/BH-template.xlsm")
        else:
            fname = os.path.join(BASE_DIR, "excel/json/export/qbe_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/QBE-template.xlsm")

        with open(fname) as myfile:
            mapping = json.load(myfile)
        self.mapping = mapping

        # template for exporting
        if carrier == "BH":
            self.export_reference = bh_format
        else:
            self.export_reference = qbe_format

        # apply naming convention the workbook
        if self.carrier == "BH":
            carrier = "BH"
        else:
            carrier = "QBE"
        outfile = "export-{pk}-{carrier}-{num}.xlsm".format(pk=pk, carrier=carrier, num=randint(100, 1000))
        outfile = os.path.join(BASE_DIR, 'tmp', outfile)
        self.outfile = outfile

        # creating a copy of the template and saving it as the outfile
        # allows other processes to read the blank template workbook
        # without any conflicting issues
        if os.path.exists(outfile):
            os.remove(outfile)
        shutil.copyfile(self.template, outfile)

        # create logger #
        self.logger = create_logger(pk=pk, wb_type='risk_eval')
        self.logger.info("Section B Export User: {}  PK: {}  carrier: {}".format(user_id, pk, carrier))

    def risk_eval(self,request):
        # Risk Eval sheet
        self.sheet = self.wb.sheets['Risk Eval']
        ## --- run all model --- ##
        self.ExportA()

        self.ExportB()

        self.ReadB(request)

        #self.ExportExmod()
        #self.ReadExmod()

        return 0

    def open_workbook(self):
        # create a new app with seperate PID from other workbooks
        # that might be created from multiple users using this app
        pythoncom.CoInitialize() # workbooks do not open up without this; need to investigate further!
        app = xl.App()
        self.logger.info("New App Created")
        self.app = app
        # close the initial blank book
        book = self.app.books[0]
        book.close()
        # then, open your workbook template
        self.wb = self.app.books.open(self.outfile)
        self.logger.info("Workbook {} is open\n".format(self.outfile))
        return app


    def save_and_exit(self):
        self.logger.info("Saving and Exiting")
        self.wb.save()
        self.wb.close() # close the initial workbook
        pid = self.app.pid
        # first attempt closing the workbook through xlwings
        self.app.quit()
        self.logger.info("Workbook ({}) closed via `app.quit()`".format(pid))
        # then close the workbook via system
        os_kill_result = os.system("tskill {}".format(pid))
        # non-zero exit means error
        self.logger.info("Workbook ({}) closed via system. Success: {}".format(pid, os_kill_result))

        self.close_logger()

    def close_logger(self):
        # turn off logger
        self.logger.info("Closing logger handlers")
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


    def ExportA(self):
        """
        Section A. General Information
        """
        self.logger.info("Section A")
        sectionA = self.mapping["Risk Eval"]['SectionA']
        general_info_fields = sectionA['general info']
        sheet = self.sheet

        self.logger.info("about to start writing for Section A")
        instance_generalinfo = models.GeneralInfo.objects.get(pk = self.pk)
        self.generalinfo = instance_generalinfo
        q = instance_generalinfo.__dict__ # convert the query to a dictionary
        for field, loc in general_info_fields.items():
            val = q.get(field, '') # get the value
            if field == 'state':
                val = states.get(val)
            # if there is data, then
            if loc:
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val

        ## Manual Premium Lines ##
        self.logger.info("Section A -- Manual Premium Lines")
        if self.carrier == 'BH':
            manual_premium_fields = sectionA['manual premium'].values()
            qset = models.GeneralInfoPremium.objects.filter(generalinfo = instance_generalinfo)[:5] # Took comment off to put [:5] back, 6/8/22

            for i, (row, query) in enumerate(zip(manual_premium_fields, qset), start=1):
                query = query.__dict__
                if i == 1:
                    field = "manual_premium"
                    loc = row[field]
                    val = query.get(field)
                    self.logger.info("-- {}. {}:  Range({})  Value: {}".format(i, field, loc, val))
                    sheet.range(loc).value = val
                else:
                    for field, loc in row.items():
                        val = query.get(field)
                        self.logger.info("-- {}. {}:  Range({})  Value: {}".format(i, field, loc, val))
                        sheet.range(loc).value = val
            
            # Add Class Calc export to do certain calculations for Section B, 6/8/22
            self.sheet = self.wb.sheets['Class Calc - Extra Classes']
            sheet = self.sheet
            manual_premium_fields_for_extra_class_codes = self.mapping["Class Calc - Extra Classes"]['extra_class_codes'].values()
            qset = models.GeneralInfoPremium.objects.filter(generalinfo = instance_generalinfo)[5:]
            for i, (row, query) in enumerate(zip(manual_premium_fields_for_extra_class_codes, qset), start=6):
                query = query.__dict__
                for field, loc in row.items():
                    val  = query.get(field)
                    sheet.range(loc).value = val
            self.sheet = self.wb.sheets['Risk Eval']

    def ExportB(self):
        """
        Account History and Loss History
        """
        self.logger.info("Section B")
        self.logger.info("Section B. Account History")
        sheet = self.sheet
        generalinfo = self.generalinfo

        # get fields and Excel cell locations from JSON file
        sectionB_fields = self.mapping["Risk Eval"]['SectionB']
        account_history_fields = sectionB_fields['account history']
        lossrating_valuation_fields = sectionB_fields['loss rating']

        qset = models.AccountHistory.objects.filter(generalinfo = generalinfo)
        for policy_period, row_fields in account_history_fields.items():
            query = qset.filter(policy_period = int(policy_period))
            if len(query):
                query = query[0]
                if query.no_history:
                    self.logger.info("Policy Period: {} is skipped -- no history".format(policy_period))
                    # populate policy periods with no data with blanks
                    for field, loc in row_fields.items():
                        # you can't edit in actual loss ratio or policy period number
                        if not field in ('actual_loss_ratio', 'policy_period',):
                            val = ''
                            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                            sheet.range(loc).value = val
                else:
                    query = query.__dict__
                    self.logger.info("Policy Period: {} -- history available".format(policy_period))
                    for field, loc in row_fields.items():
                        # you can't edit in actual loss ratio or policy period number
                        if not field in ('actual_loss_ratio', 'policy_period',):
                            val = query.get(field, '')
                            
                            # Removing val to assure we pass in proper null values to temp, 2/26/22, ljh
                            #if val and loc:
                            if loc:
                                # Add code to switch None to '', Doorn, 2/27/2022
                                if val == None:
                                    val = ''

                                # if there is a value and loc range, then populate
                                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                                sheet.range(loc).value = str(val)
            else:
                for field, loc in row_fields.items():
                    # you can't edit in actual loss ratio or policy period number
                    if not field in ('actual_loss_ratio', 'policy_period',):
                        val = '' # populate policy periods with no data with blanks
                        self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                        sheet.range(loc).value = val

        self.logger.info("Section B. Loss Rating")
        qset = models.LossRatingValuation.objects.filter(generalinfo = generalinfo)
        for policy_period, row_fields in lossrating_valuation_fields.items():
            query = qset.filter(policy_period = int(policy_period))
            if len(query):
                query = query[0]
                if query.no_history:
                    self.logger.info("Policy Period: {} is skipped -- no history".format(policy_period))
                    # populate policy periods with no data with blanks
                    for field, loc in row_fields.items():
                        # you can't edit in actual loss ratio or policy period number
                        if not field in ('actual_loss_ratio', 'policy_period',):
                            val = ''
                            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                            sheet.range(loc).value = val
                else:
                    query = query.__dict__
                    self.logger.info("Policy Period: {} -- history available".format(policy_period))
                    for field, loc in row_fields.items():
                        # you can't edit in actual loss ratio or policy period number
                        if not field in ('actual_loss_ratio', 'policy_period',):
                            val = query.get(field, '')

                            # Removing val to assure we pass in proper null values to temp, 2/26/22, ljh
                            #if val and loc:
                            if loc:
                                # Add code to switch None to '', Doorn, 2/27/2022
                                if val == None:
                                    val = ''

                                # if there is a value and loc range, then populate
                                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                                sheet.range(loc).value = str(val)
            else:
                for field, loc in row_fields.items():
                    # you can't edit in actual loss ratio or policy period number
                    if not field in ('actual_loss_ratio', 'policy_period',):
                        val = '' # populate policy periods with no data with blanks
                        self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                        sheet.range(loc).value = val

    def ReadB(self,request):
        """
        Account History and Loss History
        """
        generalinfo = self.generalinfo
        self.logger.info("READING Section B")
        self.logger.info("READING Section B. Account History")
        sheet = self.sheet
        reference = self.export_reference
        account_history_fields = reference['account history']
        loss_fields = reference['loss rating']
        self.logger.info("Fields mapping was read")
        data = {}
        row_count = 0
        # Set up data validator #
        validator = DataValidator(model = models.AccountHistory)
        acchist_queryset = models.AccountHistory.objects.filter(generalinfo = self.generalinfo).order_by('-effective_date')

        # Removed below as not required for processing in this section, 5/18/22
        """for instance, (_, row) in zip(acchist_queryset, account_history_fields.items()):
            for field, loc in row.items():
                val = sheet.range(loc).value
                val = validator.review(field_name=field, value=val)
                setattr(instance, field, val)
            try:
                pass
                #instance.save()
            except:
                print("ERROR: ", field, "--", val)
                print(instance.__dict__)
            row_count+=1 """

        # Account History data to be sent to HTML template
        account_history_data = {}
        for i, row in account_history_fields.items():
            data = {}
            for field, loc in row.items():
                val = sheet.range(loc).value
                if field == "actual_loss_ratio" and val:
                    val = 100*val
                data[field] = val
            account_history_data[i] = data

        """ if account_history_data['average all years']['incurred_losses'] == None:
            if  account_history_data['totals']['incurred_losses'] is not None:
                account_history_data['average all years']['incurred_losses'] = account_history_data['totals']['incurred_losses']/row_count
            else:
                 account_history_data['average all years']['incurred_losses'] = 0

        if  account_history_data['totals']['paid_losses'] is not None:
            account_history_data['average all years']['paid_losses'] = account_history_data['totals']['paid_losses']/row_count
        else:
            account_history_data['average all years']['incurred_losses'] = 0


        if  account_history_data['totals']['total_claims'] is not None:
            account_history_data['average all years']['total_claims'] = account_history_data['totals']['total_claims']/row_count
        else:
            account_history_data['average all years']['total_claims'] = 0

        if  account_history_data['totals']['total_indemnity_claims'] is not None:
            account_history_data['average all years']['total_indemnity_claims'] = account_history_data['totals']['total_indemnity_claims']/row_count
        else:
            account_history_data['average all years']['total_indemnity_claims'] = 0

        if  account_history_data['totals']['indemnity_claims'] is not None:
            account_history_data['average all years']['indemnity_claims'] = account_history_data['totals']['indemnity_claims']/row_count
        else:
                account_history_data['average all years']['indemnity_claims'] = 0

        if  account_history_data['totals']['open_claims'] is not None:
            account_history_data['average all years']['open_claims'] = account_history_data['totals']['open_claims']/row_count
        else:
            account_history_data['average all years']['open_claims'] = 0

        if account_history_data['totals']['written_premium'] is None or account_history_data['totals']['written_premium'] == '':
            account_history_data['totals']['written_premium'] = 0

        for i in range(1,6):
            if account_history_data[str(i)]['written_premium'] == None:
                account_history_data[str(i)]['written_premium'] = 0

        if  account_history_data['totals']['written_premium'] is not None and account_history_data['totals']['written_premium'] is not '':
            account_history_data['average all years']['written_premium'] = account_history_data['totals']['written_premium']/row_count
        else:
            account_history_data['average all years']['written_premium'] = 0 """

        self.account_history_data = account_history_data
        #self.logger.info("Section B. Loss Rating")
        loss_fields = reference['loss rating']
        validator = DataValidator(model = models.LossRatingValuation)
        loss_queryset = models.LossRatingValuation.objects.filter(generalinfo = generalinfo).order_by('-policy_period')

        # Removed below as not required for processing in this section, 5/18/22
        """for instance, (_, row) in zip(loss_queryset, loss_fields.items()):
            for field, loc in row.items():
                val = sheet[loc].value
                val = validator.review(field_name=field, value=val)
                setattr(instance, field, val)

            try:
                #instance.save()
                pass
            except:
                print("ERROR SAVING INSTANCE: ", field, "--", val)
                print(instance.__dict__) """

        loss_data = {}
        # Loss data to be sent to HTML template
        # outfile = 'qiBwKr.xlsm'
        # outfile = os.path.join(BASE_DIR, 'tmp', outfile)
        # self.outfile = outfile
        # self.wb = self.app.books.open(self.outfile)
        # sheet = self.sheet = self.wb.sheets['Risk Eval']

        for i, row in loss_fields.items():
            data = {}
            for field, loc in row.items():
                val = sheet[loc].value
                if (field == "bh_developed_loss_ratio" or  field == "qbe_developed_loss_ratio") and val:
                    val = 100*val
                data[field] = val

            # Removed below as it doesn't seem to make sense
            """if request.session.has_key('instance_generalinfo'):
                instance_generalinfo = request.session['instance_generalinfo'] 
                instance_generalinfo = models.GeneralInfo.objects.get(pk = instance_generalinfo) 
            try:
                loss_queryset = models.LossRatingValuation.objects.filter(generalinfo = instance_generalinfo, policy_period=data['policy_period']).order_by('policy_period')
                data['valuation_date'] = loss_queryset[0].valuation_date
            except:
                pass    """
                
            loss_data[i] = data
        """ try:
            for i in range(1,6):
                if loss_data[str(i)]['ultimate_reported_claims'] is not None:
                    loss_data[str(i)]['ultimate_reported_claims'] =float(str(loss_data[str(i)]['ultimate_reported_claims'])[:str(loss_data[str(i)]['ultimate_reported_claims']).find('.')+3])

                if loss_data[str(i)]['ultimate_indemnity_claims'] is not None:
                    loss_data[str(i)]['ultimate_indemnity_claims'] = float(str(loss_data[str(i)]['ultimate_indemnity_claims'])[:str(loss_data[str(i)]['ultimate_indemnity_claims']).find('.')+3])

            if loss_data['analysis']['ultimate_reported_claims'] is not None:
                loss_data['analysis']['ultimate_reported_claims'] = float(str(loss_data['analysis']['ultimate_reported_claims'])[:str(loss_data['analysis']['ultimate_reported_claims']).find('.')+3])

            if loss_data['analysis']['ultimate_indemnity_claims'] is not None:
                loss_data['analysis']['ultimate_indemnity_claims'] = float(str(loss_data['analysis']['ultimate_indemnity_claims'])[:str(loss_data['analysis']['ultimate_indemnity_claims']).find('.')+3])

        except Exception as e:
            print(e) """
        self.loss_data = loss_data

    def ExportExmod(self):
        """
        Risk Characteristics
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info

        # get fields from JSON
        sectionC_fields = self.mapping["Risk Eval"]['SectionC']
        risk_exmod_fields = sectionC_fields['exmod'].values()

        if self.carrier == "QBE":
            sheet.range('J38').value = generalinfo.effective_date.year
        qset = models.RiskExmod.objects.filter(generalinfo = generalinfo).order_by('-year')
        if len(qset):
            for row, query in zip(risk_exmod_fields, qset):
                if query.no_history:
                    self.logger.info("-- {}:  Range({})  Value: No History for {}".format('exmod_val', loc, query.year))
                else:
                    query = query.__dict__
                    loc = row['exmod_val']
                    val = query.get('exmod_val')
                    self.logger.info("-- {}:  Range({})  Value: {}".format('exmod_val', loc, val))
                    sheet.range(loc).value = val


    def ReadExmod(self):
        """
        Account History and Loss History
        """
        generalinfo = self.generalinfo
        self.logger.info("Section C")
        self.logger.info("Section C. Exmod")
        sheet = self.sheet
        reference = self.export_reference
        exmod_fields = reference['exmod']

        # Account History data to be sent to HTML template
        validator = DataValidator(model = models.RiskExmod)
        exmod_qset = models.RiskExmod.objects.filter(generalinfo = generalinfo).order_by('-year')
        for instance, (_, row) in zip(exmod_qset, exmod_fields.items()):
            for field, loc in row.items():
                val = sheet.range(loc).value
                val = validator.review(field_name=field, value=val)
                instance.loss_rate = val
            self.logger.info("-- WRITING {}:  Range({})  Value: {}".format(field, loc, val))
            instance.save()
