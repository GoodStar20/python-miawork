
from asyncio.windows_events import NULL
import os
import pythoncom
import xlwings as xl
import random
from django.contrib.auth.models import User
from risk_eval import models
from .data_validation import DataValidator, state_name_to_abbreviation
from time import sleep
import json
import logging
from schedule_rating import models as sr_models
from decimal import Decimal
import datetime

# Import to do the now() and get current date/time
from datetime import datetime as dtt

formatter = logging.Formatter('%(asctime)s - %(message)s')

def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

def handle_uploaded_file(f):
    # temporary workbook
    fname = "tmp/workbook_{}.xlsm".format(random.randint(0, 1000000))
    with open(fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return fname

def create_logger(pk):
    # logging parameters #
    file_handler = logging.FileHandler("tmp/excel_upload_{}.log".format(pk))
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

class Upload:
    def __init__(self, fname, user_id, upload_id, kind, cleanup=True):
        self.fname = fname
        self.user_id = user_id # user ID
        self.upload_id = upload_id
        self.kind = kind
        self.cleanup = cleanup
    
        if kind == "BH":
            mapping_fname = "excel/json/upload/bh_format.json"
        else:
            mapping_fname = "excel/json/upload/qbe_format.json"

        with open(mapping_fname) as myfile:
            mapping = json.load(myfile)
        self.mapping = mapping
        # create logger #
        self.logger = create_logger(self.upload_id)
        self.logger.info("NEW IMPORT User: {}  Kind: {}".format(user_id, kind))

    def open_workbook(self):
        # Create a new app with seperate PID from other workbooks
        # That might be created from multiple users using this app
        pythoncom.CoInitialize() # workbooks do not open up without this; need to investigate further!
        app = xl.App()
        self.logger.info("New App Created")
        self.app = app
        
        # Close the initial blank book
        book = self.app.books[0]
        book.close()

        # Then, open your workbook template
        self.wb = self.app.books.open(self.fname, update_links=False, read_only=True, ignore_read_only_recommended=True)
        self.logger.info("Workbook {} is open\n".format(self.fname))
        return app

    def risk_eval(self, response,unique_number,form_type,id):
        self.logger.info("Reading Data for Risk Eval")
        self.sheet = self.wb.sheets['Risk Eval']

        # For Extra Large Loss sheet addition, 8/11/22 -------

        # Check if the sheet exists, if not then set to None to notify below, 8/24/22
        #if 'Extra Lrg Losses' in self.wb.sheets:
        try:
            self.sheet_extra_losses = self.wb.sheets['Extra Lrg Losses']
        except:
            self.sheet_extra_losses = None

        # End addition -----

        self._sectionA(response,unique_number,form_type,id) # returns generalinfo.id
        self._sectionB(response,unique_number)
        self._sectionC(response,unique_number)
        self._sectionD(response,unique_number) 
        self._sectionF(response,unique_number)
        self._sectionG(response,unique_number)
        self._sectionH(response,unique_number)

    def uw_specialty(self,response,unique_number,id):
        self._score(response,unique_number)
        self._wood_mechanical(response,unique_number)
        self._wood_manual(response,unique_number)
        self._logging(response,unique_number)

    def exit(self):
        # exit open workbook
        app = self.app
        pid = self.app.pid
        app.quit()
        if self.cleanup:
            for i in range(4):
                if os.path.exists(self.fname):
                    try:
                        # use sleep to create a gap between quitting the application and removing the application
                        sleep(5)
                        self.logger.error("Attempting to remove {}".format(self.fname))
                        os.remove(self.fname) # delete workbook so things don't build up
                    except:
                        os.system("tskill {}".format(pid))
                        self.logger.error("Attempt {}: Can't remove tmp file {}".format(i, self.fname))
        self.logger.info("Successful upload!")
        self.close_logger()

    def close_logger(self):
        # turn off logger
        self.logger.info("Closing logger handlers")
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def check_general_info_exists(self):
        """
        Check if data already exists in the database
        """
        sheet = self.wb.sheets['Risk Eval']
        data = dict()
        reference = self.mapping["Risk Eval"]['SectionA']
        general_info_fields = reference["general info"]
        ## Set up data validator
        validator = DataValidator(model = models.GeneralInfo)
        for field, loc in general_info_fields.items():
            if loc:
                val = sheet.range(loc).value
                if field == "state":
                    val = state_name_to_abbreviation(val)
                elif field == "projected_payroll" or field == "projected_net_premium":
                    if val is not None and is_float(val) == True:
                        val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        val = None
                data[field] = validator.review(field_name=field, value=val)
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        general_infos = models.GeneralInfo.objects.filter(unique_number = data['unique_number'])
        
        if general_infos.exists():
            return 'Update', data['unique_number'], general_infos
        else:
            return 'Create', data['unique_number'], ''

    def _sectionA(self,response,unique_number,form_type,id):
        """
        Section A. General Information
        """
        sheet = self.sheet
        data = dict()
        reference = self.mapping["Risk Eval"]['SectionA']
        general_info_fields = reference["general info"]

        # Set up data validator
        validator = DataValidator(model = models.GeneralInfo)
        for field, loc in general_info_fields.items():
            if loc:
                val = sheet.range(loc).value
                if field == "state":
                    val = state_name_to_abbreviation(val)
                elif field == "projected_payroll" or field == "projected_net_premium" or field == 'projected_base_premium':
                    if val is not None and is_float(val) == True:
                        val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        # Set these to zero vs. None to allow the entry to process (zero is the default in the template), 6/11/22
                        val = 0
                data[field] = validator.review(field_name=field, value=val)
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        data['created_by'] = self.user_id
        data['last_modified_by'] = self.user_id
        data['carrier'] = form_type
        data['upload_id'] = self.upload_id

        if not data['governing_class_code'] == None:
            if is_float(data['governing_class_code']) == True:
                data['governing_class_code'] = int(data['governing_class_code'])
            
        # Add code to handle Agency Name which is missing from QBE files, Doorn, 2/27/2022
        if self.kind == 'QBE':
            data['agency_name'] = ''

        if data['term_frequency'] == 'Per Agent ':
            data['term_frequency'] = 'Per Agent'
        
        if response == 'Update':
            # Save data
            generalinfo = models.GeneralInfo.objects.filter(id = id).update(**data)
            generalinfo = models.GeneralInfo.objects.filter(id = id)
            generalinfo = generalinfo.first()
            self.logger.info("update: {}\n".format(generalinfo))
        else:
            generalinfo = models.GeneralInfo.objects.create(**data)
            self.logger.info("Saved: {}\n".format(generalinfo))
       
        if self.kind == "BH":
            ## Manual Premium Lines ##
            self.logger.info("Section A -- Manual Premium Lines")
            # Set up data field validator #
            validator = DataValidator(models.GeneralInfoPremium)
            count = 0
            manual_premium_fields = reference['manual premium']
            for _, row in manual_premium_fields.items():
                line_data = dict()
                for field, loc in row.items():
                    val = sheet.range(loc).value
                    if field == "manual_premium":
                        if val is not None and is_float(val) == True:
                            val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                        else:
                            val = None
                    line_data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                
                # Grab user id
                line_data['last_modified_by'] = self.user_id
                
                # Changed check to look for state and class code to allow save, 6/11/22
                #if line_data['manual_premium'] is not None:
                if (line_data['state'] is not None) and (line_data['class_code'] is not None):
                    #if line_data['manual_premium'] >= 0:
                    if response == 'Update': 
                        instance = models.GeneralInfoPremium.objects.filter(generalinfo = generalinfo)[count]
                        generalinfopremium = models.GeneralInfoPremium.objects.filter(id = instance.id).update(**line_data)
                        count+=1
                    else:
                        instance = models.GeneralInfoPremium.objects.create(generalinfo = generalinfo, **line_data)
                        
                    self.logger.info("Saved: {}\n".format(instance))

            sheet = self.wb.sheets['Class Calc - Extra Classes']            
            reference = self.mapping["Class Calc - Extra Classes"]['extra_class_codes']
            extra_class_codes = reference
            for _, row in extra_class_codes.items():
                line_data = dict()
                for field, loc in row.items():
                    val = sheet.range(loc).value
                    if field == "manual_premium":
                        if val is not None:
                            try:
                                val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                            except Exception as e:
                                print(e)
                    line_data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                
                # Grab user id
                line_data['last_modified_by'] = self.user_id

                # Changed check to look for state and class code to allow save, 6/11/22
                #if line_data['manual_premium'] is not None:
                if (line_data['state'] is not None) and (line_data['class_code'] is not None):
                    #if line_data['manual_premium'] >= 0:
                    if response == 'Update':                            
                        try:
                            instance = models.GeneralInfoPremium.objects.filter(generalinfo = generalinfo)[count]
                            generalinfopremium = models.GeneralInfoPremium.objects.filter(id = instance.id).update(**line_data)
                            count+=1
                        except Exception as e:
                            instance = models.GeneralInfoPremium.objects.create(generalinfo = generalinfo, **line_data)
                    else:
                        instance = models.GeneralInfoPremium.objects.create(generalinfo = generalinfo, **line_data)
                        
                        self.logger.info("Saved: {}\n".format(instance)) 

        self.generalinfo = generalinfo

    def _sectionB(self,response,unique_number):
        """
        Account History and Loss History
        """
        generalinfo = self.generalinfo
        self.logger.info("Section B")
        self.logger.info("Section B. Account History")
        sheet = self.sheet
        reference = self.mapping["Risk Eval"]['SectionB']
        account_history_fields = reference['account history']
        data = {}
        count = 0 

        # Set up data validator
        validator = DataValidator(model = models.AccountHistory)

        # Create fields for last period and last effective/expiration dates
        last_policy_period = 0
        last_effective_date = None
        last_expiration_date = None

        # Check if we have an effective date value
        bool_effective_date = True

        for _, row in account_history_fields.items():
            for field, loc in row.items():  

                # Check if effective date is in spreadsheet
                # Updated for .strip() which causes None values to break, 6/11/22
                if field == 'effective_date':
                    if sheet.range(loc).value == None:
                        bool_effective_date = False
                    elif str(sheet.range(loc).value).strip() == '':
                        bool_effective_date = False
                
                # Set value for the incoming field
                val = sheet.range(loc).value

                # If there was no effective date, set fields to none
                if bool_effective_date == False:
                    # No effective date, set field values to None
                    data[field] = None                    
                else:
                    # There is data, process it
                    if field == 'written_premium' or field == 'incurred_losses' or field == 'paid_losses':
                        if val is not None:
                            if validator.validate_numeric(val) != None:
                                val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                            else:
                                val = None
                    
                    # Process fields from Excel file, as-is
                    data[field] = validator.review(field_name=field, value=val)
                
                # Log the entry
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
                
            # Check if there is a policy period value
            # Update to have a Period for the database
            if data['policy_period'] == None: 
                if last_policy_period == 0:
                    data['policy_period'] = 1

                    # Set for next loop
                    last_policy_period = data['policy_period'] 
                else:
                    data['policy_period'] = last_policy_period + 1

                    # Set for next loop
                    last_policy_period = data['policy_period']              
            else:
                # Set to this policy period for last on next loop
                last_policy_period = data['policy_period']

            # If no effective date, calculate effective date and expiration date for database
            # And if there was no effective date then mark record as no_history
            if bool_effective_date == False:
                if last_effective_date == None:
                    
                    # Set effective and expiration from general info table
                    effective_date = generalinfo.effective_date
                    expiration_date = generalinfo.expiration_date

                    # Subtract 1 year to store for this period's row
                    data['effective_date'] = datetime.date(effective_date.year - 1, effective_date.month, effective_date.day)
                    data['expiration_date'] = datetime.date(expiration_date.year - 1, expiration_date.month, expiration_date.day)

                else:
                    # Set effective and expiration date based on the last
                    data['effective_date'] = datetime.date(last_effective_date.year - 1, last_effective_date.month, last_effective_date.day)
                    data['expiration_date'] = datetime.date(last_expiration_date.year - 1, last_expiration_date.month, last_expiration_date.day)
                
                # Set no history
                data['no_history'] = True
            else:
                data['no_history'] = False

            # Set user id for last modified by
            data['last_modified_by'] = self.user_id

            # Set last dates for next loop
            last_effective_date = datetime.date(data['effective_date'].year, data['effective_date'].month, data['effective_date'].day)
            last_expiration_date = datetime.date(data['expiration_date'].year, data['expiration_date'].month, data['expiration_date'].day)
                    
            # Reset bool_effective_date for next loop
            bool_effective_date = True

            if not data['policy_period'] == None: 
                if response == 'Update':                    
                    instance = models.AccountHistory.objects.filter(generalinfo = generalinfo)
                    if instance.exists():
                        try:
                            instance = instance[count]
                            # Changed accout_history = to instance =, Doorn, 2/27/2022
                            instance = models.AccountHistory.objects.filter(id = instance.id).update(**data)
                            count +=1
                        except:
                            pass     
                else:
                    instance = models.AccountHistory.objects.create(generalinfo = generalinfo, **data)

                self.logger.info("Saved: {}\n".format(instance))
        
        # Set count to zero for Loss Rating looping below
        count = 0 

        self.logger.info("Section B. Loss Rating")
        loss_rating_fields = reference['loss rating']
        validator = DataValidator(model = models.LossRatingValuation)

        # Reset policy period check
        last_policy_period = 0
        
        # Set instance of account history to check if no_history for a row
        instanceAcctHx = models.AccountHistory.objects.filter(generalinfo = generalinfo)

        for _, row in loss_rating_fields.items():
            data = {}

            for field, loc in row.items():
                
                # Set value for the incoming field
                val = sheet.range(loc).value
               
                if field == 'payroll':
                    if val is not None and is_float(val) == True:
                        val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        val = None

                # Process data field from spreadsheet, as-is
                data[field] = validator.review(field_name=field, value=val)

                # Log processs step in logger
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Check if there is a policy period value
            # Update to have a Period for the database
            if data['policy_period'] == None: 
                data['valuation_date'] = None
                if last_policy_period == 0:
                    data['policy_period'] = 1

                    # Set for next loop
                    last_policy_period = data['policy_period'] 
                else:
                    data['policy_period'] = last_policy_period + 1

                    # Set for next loop
                    last_policy_period = data['policy_period']              
            else:
                # Set to this policy period for last on next loop
                last_policy_period = data['policy_period']
            
            # Check if the row is a no history scenario
            if instanceAcctHx.filter(policy_period = data['policy_period']).first().no_history == True:
                # Set no history 
                data['no_history'] = True

                # Set rest of vars to nothing
                data['valuation_date'] = None
                data['payroll'] = None
                data['prior_carrier'] = None
            else:
                data['no_history'] = False

            # Set the user that made the update
            data['last_modified_by'] = self.user_id

            if data['policy_period']:
                if response == 'Update':                    
                    instance = models.LossRatingValuation.objects.filter(generalinfo = generalinfo)
                    if instance.exists():
                        try:
                            instance = instance[count]
                            # Changed lossrating = to instance =, Doorn, 2/27/2022
                            instance = models.LossRatingValuation.objects.filter(id = instance.id).update(**data)
                            count +=1
                        except:
                            pass    
                else:
                    instance = models.LossRatingValuation.objects.create(generalinfo = generalinfo, **data)

                # Log loss rating save process
                self.logger.info("Saved: {}\n".format(instance))
        
        # Adding New Processing Rules, 4/16/22 ------------------------------

        # Pulling loss data for this risk eval
        instanceLossX = models.LossRatingValuation.objects.filter(generalinfo = generalinfo)

        # Looping Account History Periods
        for index, item in enumerate(instanceAcctHx):
            data = {}

            # Filter to Period of Loss Data table
            lossXItem = instanceLossX.filter(policy_period = item.policy_period).first()
            
            # Check if criteria met for Rule #1
            if (
                self.kind == 'QBE' 
                and not item.effective_date == None
                and not item.expiration_date == None
                and not item.total_indemnity_claims == None
                and not item.indemnity_claims == None
                and not item.open_claims == None
            ): 
                if ( 
                    not lossXItem.valuation_date == None
                    and not lossXItem.payroll == None
                    and not lossXItem.prior_carrier == None
                ):
                    if item.incurred_losses == None:
                        data['incurred_losses'] = 0
                    if item.paid_losses == None:
                        data['paid_losses'] = 0
                    if item.total_claims == None:
                        data['total_claims'] = 0
                    
                    # Save data when meeting criteria for Rule #1
                    instance = models.AccountHistory.objects.filter(id = item.id).update(**data)
                    
                    # Add log message for save
                    self.logger.info("Saved: {}\n".format(instance))
            
            # Check if criteria is met for Rule #3 (note this covers Rule # 2 as well)
            if(item.written_premium == None):
                data = {}
                lossData = {}

                # Second set of values to check for Rule #3
                if ( 
                    lossXItem.valuation_date == None
                    and lossXItem.payroll == None
                    and (
                        lossXItem.prior_carrier == None 
                        or lossXItem.prior_carrier in ['N/A', 'None', 'none', 'na', 'NA', 'Not Applicable', 'n/a', 'not applicable', 'no prior', 'No Prior', 'No prior']
                    )
                ):
                    
                    # Rule #2/3 criteria met, update results for rule                     
                    data['no_history'] = True
                    data['written_premium'] = None
                    data['incurred_losses'] = None
                    data['paid_losses'] = None
                    data['total_claims'] = None
                    data['total_indemnity_claims'] = None
                    data['indemnity_claims'] = None
                    data['open_claims'] = None
                    
                    lossData['prior_carrier'] = None               
                    lossData['no_history'] = True

                    # Update the data in the database
                    instance = models.AccountHistory.objects.filter(id = item.id).update(**data)
                    lossInstance = models.LossRatingValuation.objects.filter(id = lossXItem.id).update(**lossData)

                    # Send logger saved success
                    self.logger.info("Saved: {}\n".format(instance))
                    self.logger.info("Saved: {}\n".format(lossInstance))
 
    def _sectionC(self,response,unique_number):
        """
        Risk Characteristics
        """
        generalinfo = self.generalinfo
        self.logger.info("Section C")
        self.logger.info("Section C. Risk Characteristics")
        sheet = self.sheet
        reference = self.mapping["Risk Eval"]['SectionC']
        risk_characteristic_fields = reference['risk characteristics']
        
        data = {}
        validator = DataValidator(model = models.RiskHeader)

        for field, loc in risk_characteristic_fields.items():
            val = sheet.range(loc).value

            # Convert N/A for financial_indicators field
            if field == 'financial_indicators': 
                if val == 'N/A':
                    val = 'Not Applicable'
                else:
                    # Added None check that was causing break when .strip() applied, 6/11/22
                    if val != None:
                        # Added below to remove extra whitespaces
                        val = val.strip()

            data[field] = validator.review(field_name=field, value=val)
            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        if response == 'Update':
            
            # Update dataset
            instance = models.RiskHeader.objects.filter(generalinfo = generalinfo).update(**data)    
        else:
            instance = models.RiskHeader.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

        self.logger.info("Section C. Exmod")
        data = {}
        validator = DataValidator(model = models.RiskExmod)
        count = 0
        exmod_fields = reference['exmod']
        for _, row in exmod_fields.items():
            for field, loc in row.items():
                val = sheet.range(loc).value
                if field == "year" and isinstance(val, (int, float)):
                    val = int(val)
                data[field] = validator.review(field_name=field, value=val)
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Grab the last user updated
            data['last_modified_by'] = self.user_id

            if response == 'Update':                
                instance = models.RiskExmod.objects.filter(generalinfo = generalinfo)
                if instance.exists():
                    instance = instance[count]
                    riskexmod = models.RiskExmod.objects.filter(id = instance.id).update(**data)
                    count +=1
            else:
                instance = models.RiskExmod.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))

    def _sectionD(self,response,unique_number):
        """
        Section D. Checklist
        """
        generalinfo = self.generalinfo
        self.logger.info("Section D. Checklist")
        sheet = self.sheet
        checklist_fields = self.mapping["Risk Eval"]['SectionD']
        data = {}

        validator = DataValidator(model = models.Checklist)

        for field, loc in checklist_fields.items():
            val = sheet.range(loc).value
            data[field] = validator.review(field_name=field, value=val)
            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        if data['date_signed_wc_acord130'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['date_signed_wc_acord130'] = None
        
        if data['supplemental_application_year'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['supplemental_application_year'] = None
        
        if data['exp_date'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['exp_date'] = None
        
        if response == 'Update':            
            instance = models.Checklist.objects.filter(generalinfo = generalinfo).update(**data)
        else:        
            instance = models.Checklist.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

    def _sectionF(self,response,unique_number):
        """
        F. Underwriter's Analysis, Comments & Pricing Recommendations
        """
        generalinfo = self.generalinfo
        self.logger.info("Section F. Underwriter's Analysis, Comments & Pricing Recommendations")
        sheet = self.sheet
        comments_fields = self.mapping["Risk Eval"]['SectionF']
        data = {}
        validator = DataValidator(model = models.Comments)

        for field, loc in comments_fields.items():
            val = sheet.range(loc).value
            data[field] = validator.review(field_name=field, value=val)
            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        if response == 'Update':            
            instance = models.Comments.objects.filter(generalinfo = generalinfo).update(**data)    
        else:
            instance = models.Comments.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

    def _sectionG(self,response,unique_number):
        """
        G. Claim Details 
        """
        generalinfo = self.generalinfo
        self.logger.info("Section G. Claim Details")
        sheet = self.sheet
        reference = self.mapping["Risk Eval"]['SectionG']
        claim_detail_fields = reference['claim details']
        data = {}
        validator = DataValidator(model = models.EvalUnderwriter)

        for field, loc in claim_detail_fields.items():
            val = sheet.range(loc).value
            data[field] = validator.review(field_name=field, value=val)
            self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        # Updated to get rid of the 1/1/1900 default dates
        if data['date'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['date'] = None
       
        if data['company_approval_date'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['company_approval_date'] = None

        if data['management_date'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['management_date'] = None
        
        if response == 'Update':            
            instance = models.EvalUnderwriter.objects.filter(generalinfo = generalinfo).update(**data)
        else:
            instance = models.EvalUnderwriter.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

        self.logger.info("Section G. Claim Lines")
        data = {}
        count = 0
        validator = DataValidator(model = models.Claims)

        line_fields = reference['claim lines']
        for i, row in line_fields.items():
            for field, loc in row.items():

                # Set value based on predefined Excel cell
                val = sheet.range(loc).value
                loc_num = loc[1:3]
                
                # Check Injury Description for cell 82 and 85, due to error in Excel file
                if loc in ['C82', 'C85']:
                    if sheet.range(loc).value != None:   
                        val = sheet.range(loc).value            
                    elif sheet.range('D' + loc_num).value != None: 
                        val = sheet.range('D' + loc_num).value
                    elif sheet.range('E' + loc_num).value != None:
                        val = sheet.range('E' + loc_num).value  
                    elif sheet.range('F' + loc_num).value != None:
                        val = sheet.range('F' + loc_num).value
                    elif sheet.range('G' + loc_num).value != None:
                        val = sheet.range('G' + loc_num).value                             
                    else:
                        val = sheet.range(loc).value
                        
                # End check -----

                if field == 'paid' or field == 'incurred':
                    if validator.validate_numeric(val) != None:
                        val = int(Decimal(val).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        val = None
                data[field] = validator.review(field_name=field, value=val)
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Grab the user updating
            data['last_modified_by'] = self.user_id

            if data['doi'] == datetime.datetime(1900, 1, 1, 0, 0):
                data['doi'] = None

            if data['claimant']:
                if response == 'Update':                    
                    instance = models.Claims.objects.filter(generalinfo = generalinfo)
                    if instance.exists():
                        try:
                            instance = instance[count]
                            # Changed from claims = to instance = to try to hit save on updates, Doorn, 2/27/2022
                            instance = models.Claims.objects.filter(id = instance.id).update(**data)
                            count +=1
                        except:
                            # Same change above for claims =, here.
                            instance = models.Claims.objects.create(generalinfo = generalinfo, **data) 
                else:
                    instance = models.Claims.objects.create(generalinfo = generalinfo, **data)
                    
                self.logger.info("Saved: {}\n".format(instance))
        
        # For Extra Large Loss Addition, 8/11/22 ---------------------
        extra_losses_sheet = self.sheet_extra_losses

         # Update to check for sheet, in case using an older spreadsheet to upload, 8/24/22
        if extra_losses_sheet is not None:
            data = {}
            for rowNum in range(2,100):
                if extra_losses_sheet.range('B' + str(rowNum)).value != None and extra_losses_sheet.range('B' + str(rowNum)).value.strip() != '':
                    data['doi'] = extra_losses_sheet.range('A' + str(rowNum)).value
                    if data['doi'] == datetime.datetime(1900, 1, 1, 0, 0):
                        data['doi'] = None
                    data['claimant'] = extra_losses_sheet.range('B' + str(rowNum)).value
                    if extra_losses_sheet.range('C' + str(rowNum)).value != None:   
                        injury_description = extra_losses_sheet.range('C' + str(rowNum)).value            
                    elif extra_losses_sheet.range('D' + str(rowNum)).value != None: 
                        injury_description = extra_losses_sheet.range('D' + str(rowNum)).value
                    elif extra_losses_sheet.range('E' + str(rowNum)).value != None:
                        injury_description = extra_losses_sheet.range('E' + str(rowNum)).value  
                    elif extra_losses_sheet.range('F' + str(rowNum)).value != None:
                        injury_description = extra_losses_sheet.range('F' + str(rowNum)).value
                    elif extra_losses_sheet.range('G' + str(rowNum)).value != None:
                        injury_description = extra_losses_sheet.range('G' + str(rowNum)).value                             
                    else:
                        injury_description = extra_losses_sheet.range('C' + str(rowNum)).value
                    data['injury_description'] = injury_description
                    data['status'] = extra_losses_sheet.range('H' + str(rowNum)).value
                    data['litigated'] = extra_losses_sheet.range('I' + str(rowNum)).value
                    
                    paid = extra_losses_sheet.range('J' + str(rowNum)).value
                    if validator.validate_numeric(paid) != None:
                        paid = int(Decimal(paid).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        paid = None
                    data['paid'] = paid

                    incurred = extra_losses_sheet.range('K' + str(rowNum)).value
                    if validator.validate_numeric(incurred) != None:
                        incurred = int(Decimal(incurred).quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
                    else:
                        incurred = None
                    data['incurred'] = incurred
                    
                    
                    if response == 'Update':                    
                        instance = models.Claims.objects.filter(generalinfo = generalinfo)
                        if instance.exists():
                            try:
                                instance = instance[count]
                                instance = models.Claims.objects.filter(id = instance.id).update(**data)
                                count +=1
                            except:
                                instance = models.Claims.objects.create(generalinfo = generalinfo, **data) 
                    else:
                        instance = models.Claims.objects.create(generalinfo = generalinfo, **data)
                        
                    self.logger.info("Saved: {}\n".format(instance))
        
        # End Extra Large Loss Addition -----------------


    def _sectionH(self,response,unique_number):
        """
        H. MIA Notes
        """
        generalinfo = self.generalinfo
        self.logger.info("Section H. Notes")
        sheet = self.sheet
        reference = self.mapping["Risk Eval"]['SectionH']
        notes_fields = reference['notes']
       
        data = {}
        validator = DataValidator(model = models.Notes)

        for field, loc in notes_fields.items():
            if loc:                                
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id
       
        if data['loss_control_report_date'] == datetime.datetime(1900, 1, 1, 0, 0):
            data['loss_control_report_date'] = None
       
        if response == 'Update':                        
            instance = models.Notes.objects.filter(generalinfo = generalinfo).update(**data)    
        else:
            instance = models.Notes.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

        self.logger.info("SectionH. Renewal target rate change")
        data = {}
        validator = DataValidator(model = models.RenewalTargetRateChange)
        renewal_target_fields = reference["renewal target rate change"]

        for field, loc in renewal_target_fields.items():
            if loc:                                
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        if response == 'Update':            
            instance = models.RenewalTargetRateChange.objects.filter(generalinfo = generalinfo).update(**data)    
        else:
            instance = models.RenewalTargetRateChange.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

        self.logger.info("SectionH Actual target rate change")
        actual_renewal_fields = reference["actual renewal rate change"]
        data = {}
        validator = DataValidator(model = models.ActualRenewalRateChange)

        for field, loc in actual_renewal_fields.items():
            if loc:                                
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Grab the user updating
        data['last_modified_by'] = self.user_id

        if response == 'Update':            
            instance = models.ActualRenewalRateChange.objects.filter(generalinfo = generalinfo).update(**data)    
        else:
            instance = models.ActualRenewalRateChange.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

    def _score(self,response,unique_number):
        """
        UW Score
        """
        generalinfo = self.generalinfo
        self.logger.info("UW SCORE")
        sheet = self.wb.sheets['SCORE']
        fields = self.mapping["SCORE"]
        data = {}

        validator = DataValidator(model = models.Score)

        for field, loc in fields.items():
            if loc:
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
        
        # Set the user adding/updating
        data['last_modified_by'] = self.user_id
        
        if response == 'Update':            
            instance = models.Score.objects.filter(generalinfo = generalinfo).update(**data)
        else:
            instance = models.Score.objects.create(generalinfo = generalinfo, **data)
        self.logger.info("Saved: {}\n".format(instance))

    def _wood_mechanical(self,response,unique_number):
        """
        UW Wood Mechanical
        """
        generalinfo = self.generalinfo
        self.logger.info("UW Wood Mechanical")

        # Check if sheet is available, since older spreadsheets may be missing this type of sheet
        # Update date: 8/27/22
        try:            
            sheet = self.wb.sheets['UW NOTES WMECHANICAL']
            mapping = self.mapping["UW NOTES WMECHANICAL"]
            data = {}

            # write header
            validator = DataValidator(model = models.MechanicalHeader)
            fields = mapping['MechanicalHeader']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Set the user last adding/updating
            data['last_modified_by'] = self.user_id
            
            if response == 'Update':
                instance = models.MechanicalHeader.objects.filter(generalinfo = generalinfo).update(**data)    
            else:
                instance = models.MechanicalHeader.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))

            # write categories
            data = {} # reset data
            validator = DataValidator(model = models.MechanicalCategories)
            fields = mapping['MechanicalCategories']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Set the user adding/updating
            data['last_modified_by'] = self.user_id
            
            if response == 'Update':
                instance = models.MechanicalCategories.objects.filter(generalinfo = generalinfo).update(**data)
            else:
                instance = models.MechanicalCategories.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))
        except:
            self.logger.info("UW Wood Mechanical, no sheet available.")

    def _wood_manual(self,response,unique_number):
        """
        UW Wood Manual
        """
        generalinfo = self.generalinfo
        self.logger.info("UW NOTES WOOD MANUAL")

        # Check if sheet is available, since older spreadsheets may be missing this type of sheet
        # Update date: 8/27/22
        try:
            sheet = self.wb.sheets['UWNOTES WMANUAL']
            mapping = self.mapping["UWNOTES WMANUAL"]
            data = {}

            # write header
            validator = DataValidator(model = models.WoodManualHeader)
            fields = mapping['WoodManualHeader']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Set the user adding/updating
            data['last_modified_by'] = self.user_id
            
            if response =='Update':
                instance = models.WoodManualHeader.objects.filter(generalinfo = generalinfo).update(**data)
            else:
                instance = models.WoodManualHeader.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))

            # write categories
            data = {} # reset data
            validator = DataValidator(model = models.WoodMechanicalCategories)
            fields = mapping['WoodMechanicalCategories']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            data['last_modified_by'] = self.user_id 
            
            if response == 'Update':
                instance = models.WoodMechanicalCategories.objects.filter(generalinfo = generalinfo).update(**data)
            else:
                instance = models.WoodMechanicalCategories.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))
        except:
            self.logger.info("UW NOTES WOOD MANUAL, no sheet available.")            

    def _logging(self,response,unique_number):
        """
        UW Wood Mechanical
        """
        generalinfo = self.generalinfo
        self.logger.info("UW Logging")

        # Check if sheet is available, since older spreadsheets may be missing this type of sheet
        # Update date: 8/27/22
        try:
            sheet = self.wb.sheets['UW NOTES LOGGING']
            mapping = self.mapping["UW NOTES LOGGING"]
            data = {}

            # write header
            validator = DataValidator(model = models.LoggingHeader)
            fields = mapping['LoggingHeader']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Grab user id to post with update
            data['last_modified_by'] = self.user_id

            if response == 'Update':
                instance = models.LoggingHeader.objects.filter(generalinfo = generalinfo).update(**data)
            else:
                instance = models.LoggingHeader.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))

            # write categories
            data = {} # reset data
            validator = DataValidator(model = models.LoggingExposureCategories)
            fields = mapping['LoggingCategories']

            for field, loc in fields.items():
                if loc:
                    val = sheet.range(loc).value
                    data[field] = validator.review(field_name=field, value=val)
                    self.logger.info("-- {}:  Range({})  Value: {}".format(field, loc, val))
            
            # Grab the user adding/updating
            data['last_modified_by'] = self.user_id

            if response == 'Update':
                instance = models.LoggingExposureCategories.objects.filter(generalinfo = generalinfo).update(**data)
            else:
                instance = models.LoggingExposureCategories.objects.create(generalinfo = generalinfo, **data)
            self.logger.info("Saved: {}\n".format(instance))
        except:
            self.logger.info("UW Logging, no sheet available.")

"""
Import Schedule Rating Worksheet
"""

def handle_uploaded_file_sr(f):
    # temporary workbook
    fname = "tmp/workbook_{}.xlsm".format(int(random.random() * 10000))
    with open(fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print("Saved {}".format(fname))
    return fname

class uploadSR:

    def __init__(self, fname, user_id, upload_id):
        self.fname = fname
        self.reference = self._load_format()
        self.user_id = user_id # user ID
        self.upload_id = upload_id

    def run(self):
        self._sectionA()
        print("Section A WAS SUCCESSFUL")
        self._sectionA() # returns generalinfo.id 
        print(self.generalinfo)
        self._StateSection(generalinfo = self.generalinfo)
        print("State Section")
        print(self.wb)

        # exit open workbook
        app = xl.apps.active
        print(app)
        app.quit()
        for i in range(4):
            try:
                pass
                # use sleep to create a gap between quitting the application and removing the application
                #sleep(5)
                #os.remove(self.fname) # delete workbook so things don't build up
            except:
                print("Attempt {}: Can't remove tmp file {}".format(i, self.fname))

        return 0
    
    def _load_format(self):
        with open("excel/json/sr_format.json") as myfile:
            reference = json.load(myfile)
            return reference

    def open_workbook(self):
        template = "excel/templates/WC_SCHEDULE_RATING_template.xlsm"
        print("trying to read: {}\n".format(template))
        self.wb = xl.Book(template)
        print("Workbook {} is open\n".format(template))
        self.sheet = self.wb.sheets['Worksheet Prep']

    def _sectionA(self):
        """
        Section A
        """
        sheet = self.sheet
        data = dict()
        reference = self.reference['SectionA']
        general_info_fields = reference["general info"]
        ## Set up data validator
        validator = DataValidator(model = models.WorksheetHeader)
        for field, loc in general_info_fields.items():
            if loc:
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                print("{} = {} from {}".format(field, val, loc))
        data['created_by'] = self.user_id
        data['last_modified_by'] = self.user_id
        self.generalinfo = models.WorksheetHeader.objects.create(**data)

    def _StateSection(self, generalinfo):
        """
        Schedule Rating Worksheet
        """
        sheet = self.sheet
        reference = self.reference['StateSection']
        risk_location_fields = reference['schedule rating worksheet']
        data = {}
        ## Set up data validator
        validator = DataValidator(model = models.WorkCompLinesHeader)

        for field, loc in risk_location_fields.items():
            val = sheet.range(loc).value
            data[field] = validator.review(field_name=field, value=val)
            print("{} = {} from {}".format(field, val, loc))
        data['last_modified_by'] = self.user_id
 
        debits_credits_fields = reference['worksheet table']
        validator = DataValidator(model = models.WorkCompLines)
        for _, row in debits_credits_fields.items():
            data = {}
            for field, loc in row.items():
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
                print("{} = {} from {}".format(field, val, loc))
            data['last_modified_by'] = self.user_id

            

