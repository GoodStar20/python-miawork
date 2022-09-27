import os
import xlwings as xl
import pythoncom 
from risk_eval import models
from schedule_rating import models as sr_models 
#from django.conf import settings # should exports be saved under MEDIA_ROOT ??
import json
import shutil
import logging
from django.conf import settings # needed to get BASE_DIR

BASE_DIR = settings.BASE_DIR


formatter = logging.Formatter('%(asctime)s - %(message)s')


states = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 
    'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 
    'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 
    'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 
    'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 
    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 
    'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 
    'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 
    'WI': 'Wisconsin', 'WY': 'Wyoming', '': ''}


def create_logger(pk, wb_type):
    """
    pk: primary key of header
    wb_type: risk_eval or schedule_rating
    """
    # logging parameters #
    file_handler_fname = os.path.join(BASE_DIR, "tmp/export-{}-{}.log".format(wb_type, pk))
    file_handler = logging.FileHandler(file_handler_fname, mode = 'w')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

def copy_to_network_drive(full_path):
    """
    Function serves to copy 
    """
    #network_drive = r'\\midwestern12.miains.net\ScannedDocs\UWWorksheets'
    network_drive = r'C:\ExportTemp'

    fname = os.path.basename(full_path)
    if os.path.isdir(network_drive):
        new_path = os.path.join(network_drive, fname)
        shutil.copyfile(full_path, new_path)
        return True
    else:
        # if the network drive doesn't exist (i.e. for testing)
        # don't worry about it
        return False


def rename_workbooks(instance_header, form_type, kind = 'risk_eval'):
    if kind == "risk_eval":
        file_type = "SUBMISSION"
    elif kind == "schedule_rating":
        file_type = "SCHEDULE"
    account_number = instance_header.account_number
    if account_number is None:
        account_number = ""
    effective_date = instance_header.effective_date.strftime("%m%d%Y")
    expiration_date = instance_header.expiration_date.strftime("%m%d%Y")
    agent_number = instance_header.agent_number
    data_set = instance_header.data_set
    # QBE has multiple form types; if not QBE then it's just 'BH'
    if form_type == "BH":
        data_set = "BH"
    unique_number = instance_header.unique_number
    term = instance_header.term
    if term == "New":
        term = "0"
    else:
        term = "1"
    uw = instance_header.uw
    quote_number = instance_header.quote_number
    #"Acct#~Effective~Expiration~agency~dataset~usub~#~underwriter-initials~File "
    file_name = f"{account_number}~{effective_date}~{expiration_date}~{agent_number}~{data_set}~{unique_number}~{term}~{uw}~{file_type}{quote_number}.xlsm"
    return file_name


class Export:
    def __init__(self, user_id, pk, form_type = 'BH', export_to_webdocs=False):
        self.user_id = user_id
        self.pk = pk
        self.form_type = form_type
        self.export_to_webdocs = export_to_webdocs

        if form_type == "BH":
            fname = os.path.join(BASE_DIR, "excel/json/export/bh_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/BH-template.xlsm")
        else:
            fname = os.path.join(BASE_DIR, "excel/json/export/qbe_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/QBE-template.xlsm")
            
        with open(fname) as myfile:
            mapping = json.load(myfile)
        self.mapping = mapping

        # apply naming convention the workbook
        instance_header = models.GeneralInfo.objects.get(pk = self.pk)
        if self.form_type == "BH":
            data_set = "BH"
        else:
            data_set = "QBE"
        outfile = rename_workbooks(instance_header, data_set, kind='risk_eval')
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
        self.logger.info("NEW EXPORT User: {}  PK: {}  form_type: {}".format(user_id, pk, form_type))

    def risk_eval(self):
        # Risk Eval sheet
        self.sheet = self.wb.sheets['Risk Eval']

        # For Extra Large Loss sheet addition, 8/11/22 -------
        self.sheet_extra_losses = self.wb.sheets['Extra Lrg Losses']
        # End addition -----

        ## --- run all model --- ##
        self.sectionA()

        self.sectionB()

        self.sectionC()

        self.sectionD()
        
        self.sectionF()

        self.sectionG()

        self.sectionH()

        ## --------------------- ##
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

        
        if self.export_to_webdocs:
            # copy the workbook to the network drive
            self.logger.info("Trying to copy '{}' to network drive".format(self.outfile))
            #if not os.path.isdir(r'\\midwestern12.miains.net\ScannedDocs\UWWorksheets'):
               # self.logger.error(r"There is no connection to \\midwestern12.miains.net\ScannedDocs\UWWorksheets")
            #self.logger.info("Connection to network drive: {}".format(os.path.isdir(r'\\midwestern12.miains.net\ScannedDocs\UWWorksheets')))
     
            if not os.path.isdir(r'C:\ExportTemp'):
               self.logger.error(r"There is no connection to C:\ExportTemp")
            self.logger.info("Connection to network drive: {}".format(os.path.isdir(r'C:\ExportTemp')))
                                  
            copy_result = copy_to_network_drive(self.outfile)
            self.logger.info("File was copied to network drive: {}".format(copy_result))
            self.exported_to_network_drive = copy_result
        else:
            self.logger.info("This is a preview. Not exporting to webdocs.")
            self.exported_to_network_drive = False
        
        self.close_logger()

    def close_logger(self):
        # turn off logger
        self.logger.info("Closing logger handlers")
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


    def sectionA(self):
        """
        Section A. General Information
        """
        self.logger.info("Section A")
        sectionA = self.mapping["Risk Eval"]['SectionA']
        general_info_fields = sectionA['general info']
        sheet = self.sheet

        self.logger.info("about to start writing for Section A")
        query_generalinfo = models.GeneralInfo.objects.get(pk = self.pk)
        q = query_generalinfo.__dict__ # convert the query to a dictionary
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
        if self.form_type == 'BH':
            manual_premium_fields = sectionA['manual premium'].values()
            qset = models.GeneralInfoPremium.objects.filter(generalinfo = query_generalinfo)[:5]
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

            self.sheet = self.wb.sheets['Class Calc - Extra Classes']
            sheet = self.sheet
            manual_premium_fields_for_extra_class_codes = self.mapping["Class Calc - Extra Classes"]['extra_class_codes'].values()
            qset = models.GeneralInfoPremium.objects.filter(generalinfo = query_generalinfo)[5:]
            for i, (row, query) in enumerate(zip(manual_premium_fields_for_extra_class_codes, qset), start=6):
                query = query.__dict__
                for field, loc in row.items():
                    val  = query.get(field)
                    sheet.range(loc).value = val
            self.sheet = self.wb.sheets['Risk Eval']

    def sectionB(self):
        """
        Account History and Loss History
        """
        self.logger.info("Section B")
        self.logger.info("Section B. Account History")
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info

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
                            if sheet.range(loc).value == None:
                                sheet.range(loc).value = 0 
                            
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


    def sectionC(self):
        """
        Risk Characteristics
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.RiskHeader.objects.filter(generalinfo = generalinfo)

        # get fields from JSON
        sectionC_fields = self.mapping["Risk Eval"]['SectionC']
        risk_characteristics_fields = sectionC_fields['risk characteristics']
        risk_exmod_fields = sectionC_fields['exmod'].values()
        
        # this method is used in case there hasn't been any data; no data --> empty query
        if len(qset):
            q = qset[0]
            q = q.__dict__

            for field, loc in risk_characteristics_fields.items():
                val = q.get(field, '')
                if loc:
                    # if there is a value and loc range, then populate
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val

        if self.form_type == "QBE":
            sheet.range('J38').value = generalinfo.effective_date.year
        qset = models.RiskExmod.objects.filter(generalinfo = generalinfo).order_by('-year')
        if len(qset):
            for row, query in zip(risk_exmod_fields, qset):
                if query.no_history:
                    # Added on 6/24/22 as loc was not set for no history scenario
                    loc = row['exmod_val']
                    self.logger.info("-- {}:  Range({})  Value: No History for {}".format('exmod_val', loc, query.year))    
                else:
                    query = query.__dict__
                    loc = row['exmod_val']
                    val = query.get('exmod_val')
                    self.logger.info("-- {}:  Range({})  Value: {}".format('exmod_val', loc, val))
                    sheet.range(loc).value = val
                

    def sectionD(self):
        """
        Checklist
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.Checklist.objects.filter(generalinfo = generalinfo)
        # get fields from JSON
        checklist_fields = self.mapping["Risk Eval"]['SectionD']

        if len(qset):
            q = qset[0]
            q = q.__dict__

            for field, loc in checklist_fields.items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val        


    def sectionF(self):
        """
        F. Underwriter's Analysis, Comments & Pricing Recommendations
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.Comments.objects.filter(generalinfo = generalinfo)

        # get fields from JSON
        comments_fields = self.mapping["Risk Eval"]['SectionF']

        if len(qset):
            q = qset[0]
            q = q.__dict__

            for field, loc in comments_fields.items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val        

    def sectionG(self):
        """
        G. Claim Details 
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info

        # Updated for Extra Large Loss Addition, 8/11/22 ------------------------
        # qset = models.Claims.objects.filter(generalinfo = generalinfo).order_by('-incurred')[:10]

        # Break large losses into the first 10 and any following
        qset = models.Claims.objects.filter(generalinfo = generalinfo).order_by('-incurred')[:10]
        qset1 = models.Claims.objects.filter(generalinfo = generalinfo).order_by('-incurred')[10:]

        sectionG_fields = self.mapping["Risk Eval"]['SectionG']
        claim_details_fields = sectionG_fields['claim details']
        claim_line_fields = sectionG_fields['claim lines'].values()

        # Process the first 10 entries
        if len(qset):
            for row, q in zip(claim_line_fields, qset):
                q = q.__dict__ # query to dict
                for field, loc in row.items():
                    val = q.get(field, '')
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val
        
        # Process the remaining entries, if any
        if len(qset1):
            extra_losses_sheet = self.sheet_extra_losses
            for i, loc in enumerate(qset1):
                q = loc.__dict__
                rowNum = i + 2
                extra_losses_sheet.range('A' + str(rowNum)).value = q.get('doi', '')
                extra_losses_sheet.range('B' + str(rowNum)).value = q.get('claimant', '')
                extra_losses_sheet.range('C' + str(rowNum)).value = q.get('injury_description', '')
                extra_losses_sheet.range('H' + str(rowNum)).value = q.get('status', '')
                extra_losses_sheet.range('I' + str(rowNum)).value = q.get('litigated', '')
                extra_losses_sheet.range('J' + str(rowNum)).value = q.get('paid', '')
                extra_losses_sheet.range('K' + str(rowNum)).value = q.get('incurred', '')

        # Process the UW evaluation data
        qset = models.EvalUnderwriter.objects.filter(generalinfo = generalinfo)
        if len(qset):
            q = qset[0]
            q = q.__dict__
            for field, loc in claim_details_fields.items():
                val = q.get(field, '')
                if loc:
                    # if there is a value and loc range, then populate
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val

    def sectionH(self):
        """
        H. MIA Notes
        """
        sheet = self.sheet
        generalinfo = models.GeneralInfo.objects.get(pk = self.pk)
        qset = models.Notes.objects.filter(generalinfo = generalinfo)
        sectionH_fields = self.mapping["Risk Eval"]['SectionH']
        notes_fields = sectionH_fields['notes']

        if len(qset):
            query = qset[0]
            query = query.__dict__
            for field, loc in notes_fields.items():
                if loc:
                    val = query.get(field, '')
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val

        renewal_target_fields = sectionH_fields['renewal target rate change']
        query = models.RenewalTargetRateChange.objects.filter(generalinfo = generalinfo)
        if len(query):
            query = query[0]
            query = query.__dict__
            for field, loc in renewal_target_fields.items():
                if loc:
                    val = query.get(field, '')
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val

        actual_renewal_fields = sectionH_fields['actual renewal rate change']
        query = models.ActualRenewalRateChange.objects.filter(generalinfo_id = self.pk)
        if len(query):
            query = query[0]
            query = query.__dict__
            for field, loc in actual_renewal_fields.items():
                if loc:
                    val = query.get(field, '')
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                    sheet.range(loc).value = val

    def uw_specialty(self):
        self.score_sheet()
        self.wood_mechanical_sheet()
        self.wood_manual_sheet()
        self.logging_sheet()
        return 0


    def score_sheet(self):
        self.logger.info("Writing SCORE sheet")
        sheet = self.wb.sheets['SCORE']
        fields = self.mapping['SCORE']

        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.Score.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__

            for field, loc in fields.items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


    
    def wood_mechanical_sheet(self):
        name = 'UW NOTES WMECHANICAL'
        self.logger.info("Writing UW NOTES WMECHANICAL sheet")
        sheet = self.wb.sheets[name]
        fields = self.mapping[name]

        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.MechanicalHeader.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Mechanical Header")
            
            for field, loc in fields["MechanicalHeader"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


        qset = models.MechanicalCategories.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Mechanical Categories")
            
            for field, loc in fields["MechanicalCategories"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


    def wood_manual_sheet(self):
        name = "UWNOTES WMANUAL"
        self.logger.info("Writing UWNOTES WMANUAL sheet")
        sheet = self.wb.sheets[name]
        fields = self.mapping[name]

        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.WoodManualHeader.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Mechanical Header")
            
            for field, loc in fields["WoodManualHeader"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


        qset = models.WoodMechanicalCategories.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Mechanical Categories")
            
            for field, loc in fields["WoodMechanicalCategories"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


    def logging_sheet(self):
        name = "UW NOTES LOGGING"
        self.logger.info("Writing UW NOTES LOGGING sheet")
        sheet = self.wb.sheets[name]
        fields = self.mapping[name]

        generalinfo = models.GeneralInfo.objects.get(pk = self.pk) ## need foreign key from General Info
        qset = models.LoggingHeader.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Logging Header")
            
            for field, loc in fields["LoggingHeader"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val


        qset = models.LoggingExposureCategories.objects.filter(generalinfo = generalinfo)

        if len(qset):
            q = qset[0]
            q = q.__dict__
            self.logger.info("Model: Logging Exposure Categories")
            
            for field, loc in fields["LoggingCategories"].items():
                val = q.get(field, '')
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                sheet.range(loc).value = val






"""
Export Schedule Rating Worksheet
"""


WB_PASSWORD = 'mIaT3mpD@ta'


class ExportSR:
    def __init__(self, user_id, pk, form_type = 'QBE', export_to_webdocs=False):
        self.user_id = user_id # needed for logging
        self.pk = pk
        self.form_type = form_type
        self.export_to_webdocs = export_to_webdocs

        if form_type == "QBE":
            fname = os.path.join(BASE_DIR, "excel/json/sr_qbe_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/SR_QBE_template.xlsm")
        else:
            fname = os.path.join(BASE_DIR, "excel/json/sr_bh_format.json")
            self.template = os.path.join(BASE_DIR, "excel/templates/SR_BH_template.xlsm")
            
        with open(fname) as myfile:
            mapping = json.load(myfile)
        self.mapping = mapping


        # rename the workbook
        instance_header = sr_models.SRHeader.objects.get(pk = self.pk)
        if self.form_type == "BH":
            data_set = "BH"
        else:
            data_set = "QBE"
        outfile = rename_workbooks(instance_header, data_set, kind='schedule_rating')
        outfile = os.path.join(BASE_DIR, 'tmp', outfile)
        self.outfile = outfile

        # creating a copy of the template and saving it as the outfile
        # allows other processes to read the blank template workbook
        # without any conflicting issues
        if os.path.exists(outfile):
            os.remove(outfile)
        shutil.copyfile(self.template, outfile)

        # create logger #
        self.logger = create_logger(pk=pk, wb_type="schedule_rating")
        self.logger.info("NEW EXPORT User: {}  PK: {}  Kind: {}".format(user_id, pk, form_type))

    def run(self):
        self._worksheet_prep()
        self._all_states()
        self.save_and_exit()
        return 0
    
    def open_workbook(self):
        # create a new app with seperate PID from other workbooks
        # that might be created from multiple users using this app
        pythoncom.CoInitialize() # workbooks do not open up without this; need to investigate further!
        app = xl.App()
        self.logger.info("Excel App {} is created\n".format(app))
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
        self.app.quit()
        self.logger.info("Workbook is saved and closed")
        self.logger.info("See {}".format(self.outfile))

        if self.export_to_webdocs:
            # copy the workbook to the network drive
            self.logger.info("Trying to copy '{}' to network drive".format(self.outfile))
            #if not os.path.isdir(r'\\midwestern12.miains.net\ScannedDocs\UWWorksheets'):
            #    self.logger.error(r"There is no connection to \\midwestern12.miains.net\ScannedDocs\UWWorksheets")
            #self.logger.info("Connection to network drive: {}".format(os.path.isdir(r'\\midwestern12.miains.net\ScannedDocs\UWWorksheets')))
            
            if not os.path.isdir(r'C:\ExportTemp'):
               self.logger.error(r"There is no connection to C:\ExportTemp")
            self.logger.info("Connection to network drive: {}".format(os.path.isdir(r'C:\ExportTemp')))
            
            copy_result = copy_to_network_drive(self.outfile)
            self.logger.info("File was copied to network drive: {}".format(copy_result))
            self.exported_to_network_drive = copy_result
        else:
            self.logger.info("This is a preview. Not exporting to webdocs.")
            self.exported_to_network_drive = False

        self.close_logger()

    def close_logger(self):
        # turn off logger
        self.logger.info("Closing logger handlers")
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


    def _worksheet_prep(self):
        """
        Export Worksheet Prep
        """
        ws_prep_fields = self.mapping["Worksheet Prep"]
        sheet = self.wb.sheets["Worksheet Prep"]
        sheet.api.Unprotect(WB_PASSWORD)

        instance_header = sr_models.SRHeader.objects.get(pk = self.pk)
        data_dict = instance_header.__dict__ # convert the query to a dictionary
        for field, loc in ws_prep_fields.items():
            val = data_dict.get(field, '')
            self.logger.info("Header -- Field {}: {} = {}".format(field, loc, val))
            sheet.range(loc).value = val

        # check off state boxes
        cell_locations = {'AL': 'O6', 'AK': 'O7', 'AZ': 'O8', 
            'AR': 'O9', 'CA': 'O10', 'CO': 'O11', 'CT': 'O12', 
            'DE': 'O13', 'D.C.': 'O14', 'GA': 'O15', 'ID': 'O16', 
            'IL': 'O17', 'IN': 'O18', 'IA': 'O19', 'KS': 'O20', 
            'KY': 'O21', 'LA': 'O22', 'ME': 'O23', 'MD': 'O24', 
            'MI': 'O25', 'MN': 'O26', 'MS': 'O27', 'MO': 'O28', 
            'MT': 'O29', 'NE': 'O30', 'NV': 'O31', 'NH': 'O32', 
            'NJ': 'O33', 'NM': 'O34', 'NY': 'O35', 'NC': 'O36', 
            'OK': 'O37', 'PA': 'O38', 'RI': 'O39', 'SC': 'O40', 
            'SD': 'O41', 'TN': 'O42', 'TX': 'O43', 'UT': 'O44', 
            'VT': 'O45', 'VA': 'O46', 'WV': 'O47'}
        sr_states = sr_models.SRStates.objects.get(header = instance_header)
        self.logger.info("Header -- States List: {}".format(sr_states.states))
        for state in sr_states.states:
            loc = cell_locations[state]
            sheet.range(loc).value = 'TRUE'
            self.logger.info("Header -- States List ({}): {} = {}".format(state, loc, val))

        if self.form_type == 'QBE':
            if instance_header.data_set in ('MP', 'WF'):
                sheet.range('N10').value = 'TRUE'
            elif instance_header.data_set in ('CE', ):
                #sheet.range('N12').value = 'TRUE'
                # this is not working right now...needs to be fixed
                pass
            else:
                # do nothing...default should be North Pointe Insurance Co.
                pass

        # protect sheet
        sheet.api.Protect(WB_PASSWORD)
        self.wb.save()
        return 0

    def _all_states(self):
        header = sr_models.SRHeader.objects.get(pk = self.pk)
        instance_states = sr_models.SRStates.objects.get(header = header)
        states = instance_states.states
        
        for state in states:
            self.logger.info("STATE: {}".format(state))
            self._write_state_section(state)
        return 0        

    def _write_state_section(self, state):
        """
        Generic function to export data to a state tab
        """ 
        # Get worksheet and unhide tab
        sheet = self.wb.sheets[state]
        sheet.api.Visible = True
        sheet.api.Unprotect(WB_PASSWORD)

        # get the mapping for the Excel fields
        try:
            worksheet_fields = self.mapping['StateSection'][state]
        except:
            self.logger.error("{} has no mapping".format(state))
        # schedule rating worksheet header has only one field
        # risk_location: C8
        header_fields = worksheet_fields['header']
        debits_credits_fields = worksheet_fields['worksheet table'].values()

        # query the data
        header = sr_models.SRHeader.objects.get(pk = self.pk)
        self.logger.info("SR Header: {}".format(header))
        # write out the header
        try:
            if state == "CA":
                state_header = sr_models.CAHeader.objects.get(header = header, state = state, 
                    form_type = self.form_type)
                qset = sr_models.CALines.objects.filter(header = state_header, state = state)
            elif state in ("AZ", "NH", "NM", "OK", "KS", "SD", "VT"):
                state_header = sr_models.AdaptedStateHeader.objects.get(header = header, state=state, 
                    form_type = self.form_type)
                qset = sr_models.AdaptedStateLines.objects.filter(header = state_header, state = state)
            else:
                state_header = sr_models.StateHeader.objects.get(header = header, state = state, 
                    form_type = self.form_type)
                qset = sr_models.StateLines.objects.filter(header = state_header, state = state)
        except:
            self.logger.error("{} has no Header or Lines object".format(state))
            return 1
        
        data_dict = state_header.__dict__
        for field, loc in header_fields.items():
            val = data_dict.get(field, '')
            if isinstance(loc, list):
                self.logger.info("Excel References: " + str(loc))
                # mapping: [Yes cell, No cell]
                if val == 'Yes' or val == "New":
                    loc = loc[0] 
                elif val == 'No' or 'Renew':
                    loc = loc[1]
                else:
                    pass
                self.logger.info("{} -- Field {}: {} = {}".format(header, field, loc, "TRUE"))
                sheet.range(loc).value = "TRUE"
            else:
                if field in ("merit_plan_credits", "merit_plan_debits", "wcpr_credits"):
                    if isinstance(val,(int,float)):
                        val = val/100
                self.logger.info("{} -- Field {}: {} = {}".format(header, field, loc, val))
                sheet.range(loc).value = val

        # write out state debit/credit lines
        self.logger.info("Writing debit/credit lines")
        if len(qset):
            for row, q in zip(debits_credits_fields, qset):
                data_dict = q.__dict__
                for field, loc in row.items():
                    # ignore range fields!
                    if field not in ("range"):
                        val = data_dict.get(field, '')
                        #adding if statement because excel is taking val as a % 
                        if isinstance(val,(int,float)):
                            val= val/100
                        self.logger.info("Writing -- Field {}: {} = {}".format(field, loc, val))
                        sheet.range(loc).value = val
        sheet.api.Protect(WB_PASSWORD)
        return 0