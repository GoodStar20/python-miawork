
from asyncio.windows_events import NULL
import xlwings as xl
import random
from risk_eval import models
from .data_validation import DataValidator
import json
from schedule_rating import models as sr_models

def handle_uploaded_file_sr(f):
    # temporary workbook
    fname = "tmp/workbook_{}.xlsm".format(int(random.random() * 10000))
    with open(fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print("Saved {}".format(fname))
    return fname

class UploadSR:
    def __init__(self, fname, user_id, upload_id, kind):
        self.fname = fname
        self.reference = self._load_format(kind)
        self.user_id = user_id # user ID
        self.upload_id = upload_id
        self.form_type = kind

    def run(self):
        self._worksheetPrep()
        self._stateSection()

        app = xl.apps.active
        print(app)
        app.quit()
    
    def _load_format(self, kind):
        if kind == "BH":
            formatFile = "excel/json/sr_bh_format.json"
        else:
            formatFile = "excel/json/sr_qbe_format.json"

        with open(formatFile) as myfile:
            reference = json.load(myfile)
            return reference

    def open_workbook(self):
        self.wb = xl.Book(self.fname)
        self.sheet = self.wb.sheets['Worksheet Prep']
        print("Workbook {} is open\n".format(self.fname))

    def _worksheetPrep(self):
        """
        Worksheet
        """
        sheet = self.sheet

        data = dict()
        worksheep_prep_fields = self.reference['Worksheet Prep']

        validator = DataValidator(model = sr_models.SRHeader)
        for field, loc in worksheep_prep_fields.items():
            if loc:
                val = sheet.range(loc).value
                data[field] = validator.review(field_name=field, value=val)
        
        data['form_type'] = self.form_type
        data['created_by'] = self.user_id
        data['last_modified_by'] = self.user_id

        generalinfo = models.GeneralInfo.objects.filter(unique_number = data['unique_number'])
        generalinfo = generalinfo.first()
        instance = sr_models.SRHeader.objects.filter(unique_number = data['unique_number'])
        self.srheader_unique_number = data['unique_number']
        if instance.exists():
            try:
                instance = instance[0]
                sr_models.SRHeader.objects.filter(id = instance.id).update(**data)
            except:
                pass
        else: 
            sr_models.SRHeader.objects.create(generalinfo = generalinfo, **data)
        

    def _stateSection(self):
        """
        Schedule Rating Worksheet
        """
        srHeader = sr_models.SRHeader.objects.filter(unique_number = self.srheader_unique_number)
        srHeader = srHeader.first()
        state_sections = self.reference['StateSection']

        states = list()
        states_data = dict()
        

        for sheet in self.wb.sheets:
            if sheet.api.Visible == -1 and sheet.name in state_sections:
                state_header_data = dict()
                state_table_data = dict()
                states.append(sheet.name)
                state_sheet = self.wb.sheets[sheet.name]
                state_header_fields = state_sections[sheet.name]['header']
                for field, loc in state_header_fields.items():
                    val = state_sheet.range(loc).value
                    if sheet.name == 'CA':
                        validator = DataValidator(model = sr_models.CAHeader)
                    elif sheet.name == 'AZ' or sheet.name == 'NH' or sheet.name == 'NM' or sheet.name == 'SD' or sheet.name == 'VT':
                        validator = DataValidator(model = sr_models.AdaptedStateHeader)
                    else:
                        validator = DataValidator(model = sr_models.StateHeader)
                    state_header_data[field] = validator.review(field_name=field, value=val)
                state_header_data['form_type'] = self.form_type
                state_header_data['state'] = sheet.name
                state_header_data['last_modified_by'] = self.user_id

                if sheet.name == 'CA':
                    instance = sr_models.CAHeader.objects.filter(state = sheet.name, header = srHeader)
                    if instance.exists():
                        try:
                            instance = instance[0]
                            sr_models.CAHeader.objects.filter(id = instance.id).update(**state_header_data)
                        except:
                            pass
                    else: 
                        sr_models.CAHeader.objects.create(header = srHeader, **state_header_data)
                elif sheet.name == 'AZ' or sheet.name == 'NH' or sheet.name == 'NM' or sheet.name == 'SD' or sheet.name == 'VT':
                    instance = sr_models.AdaptedStateHeader.objects.filter(state = sheet.name, header = srHeader)
                    if instance.exists():
                        try:
                            instance = instance[0]
                            sr_models.AdaptedStateHeader.objects.filter(id = instance.id).update(**state_header_data)
                        except:
                            pass
                    else: 
                        sr_models.AdaptedStateHeader.objects.create(header = srHeader, **state_header_data)
                else:
                    instance = sr_models.StateHeader.objects.filter(state = sheet.name, header = srHeader)
                    if instance.exists():
                        try:
                            instance = instance[0]
                            sr_models.StateHeader.objects.filter(id = instance.id).update(**state_header_data)
                        except:
                            pass
                    else: 
                        sr_models.StateHeader.objects.create(header = srHeader, **state_header_data)

                state_table_fields = state_sections[sheet.name]['worksheet table']
                if sheet.name == 'CA':
                    caHeader = sr_models.CAHeader.objects.filter(header_id = srHeader.id)
                    caHeader = caHeader.first()
                elif sheet.name == 'AZ' or sheet.name == 'NH' or sheet.name == 'NM' or sheet.name == 'SD' or sheet.name == 'VT':
                    adaptedStateHeader = sr_models.CAHeader.objects.filter(header_id = srHeader.id)
                    adaptedStateHeader = adaptedStateHeader.first()
                else:
                    stateHeader = sr_models.StateHeader.objects.filter(header_id = srHeader.id)
                    stateHeader = stateHeader.first()

                for table_key, table_value in state_table_fields.items():
                    worksheet_fields = state_table_fields[table_key]
                    for field, loc in worksheet_fields.items():                   
                        val = state_sheet.range(loc).value
                        if sheet.name == 'CA':
                            validator = DataValidator(model = sr_models.CALines)
                        elif sheet.name == 'AZ' or sheet.name == 'NH' or sheet.name == 'NM' or sheet.name == 'SD' or sheet.name == 'VT':
                            validator = DataValidator(model = sr_models.AdaptedStateLines)
                        else:
                            validator = DataValidator(model = sr_models.StateLines)
                        state_table_data[field] = validator.review(field_name=field, value=val)
                    state_table_data['category'] = table_key

                    if sheet.name == 'CA':
                        instance = sr_models.CALines.objects.filter(category = table_key, header = caHeader)
                        if instance.exists():
                            try:
                                instance = instance[0]
                                sr_models.CALines.objects.filter(id = instance.id).update(**state_table_data)
                            except:
                                pass
                        else: 
                            sr_models.CALines.objects.create(header = caHeader, **state_table_data)
                    elif sheet.name == 'AZ' or sheet.name == 'NH' or sheet.name == 'NM' or sheet.name == 'SD' or sheet.name == 'VT':
                        instance = sr_models.AdaptedStateLines.objects.filter(category = table_key, header = adaptedStateHeader)
                        if instance.exists():
                            try:
                                instance = instance[0]
                                sr_models.AdaptedStateLines.objects.filter(id = instance.id).update(**state_table_data)
                            except:
                                pass
                        else: 
                            sr_models.AdaptedStateLines.objects.create(header = adaptedStateHeader, **state_table_data)
                    else:
                        instance = sr_models.StateLines.objects.filter(category = table_key, header = adaptedStateHeader)
                        if instance.exists():
                            try:
                                instance = instance[0]
                                sr_models.StateLines.objects.filter(id = instance.id).update(**state_table_data)
                            except:
                                pass
                        else: 
                            sr_models.StateLines.objects.create(header = stateHeader, **state_table_data)   

        states_data['states'] = "".join(states)
        instance = sr_models.SRStates.objects.filter(header_id = srHeader.id)
        if instance.exists():
            try:
                instance = instance[0]
                sr_models.SRStates.objects.filter(id = instance.id).update(**states_data)
            except:
                pass
        else:
            sr_models.SRStates.objects.create(header = srHeader, **states_data)

