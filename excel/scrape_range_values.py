import xlwings as xl
import json


wb = xl.Book("templates/SR_BH_template.xlsm")

with open("json/sr_bh_format.json") as myfile:
    sr_bh_format = json.load(myfile)
    state_formats = sr_bh_format['StateSection']


data = dict()
for state, mapping in state_formats.items():
    print(state)
    table_mapping = mapping['worksheet table']
    tmp = dict()
    sheet = wb.sheets[state]
    if state != "CA":
        for cat, sheet_cells in table_mapping.items():
            range_location = sheet_cells['range'] # get the range of debit/credits
            range_value = sheet.range(range_location).value
            if isinstance(range_value , (int, float)):
                print("--> converting {} to string".format(range_value))
                range_value = str(range_value * 100) + "%"
            try:
                tmp[cat] = range_value.strip()
            except:
                print("-->", cat, range_location, range_value)
        data[state] = tmp
    sheet.api.Visible = False

data['CA'] = {'Premises': '+/-20%', 'Classification Peculiarities': '+/-20%', 
    'Medical Facilities':  '+/-20%', 'Safety Devices': '+/-20%',
    'Employees-Selection Training, Supervision': '+/-20%', 'Management-Capability/ Cooperation': '+/-20%',
    'Expense of Providing Insurance Services': '+/-20%', 'Other Factors': '+/-10%'
    }

wb.save()
wb.close()

with open("json/SR_BH_range_values.json", "w") as outfile:
    json.dump(data, outfile)



wb = xl.Book("templates/SR_QBE_template.xlsm")

with open("json/sr_qbe_format.json") as myfile:
    sr_bh_format = json.load(myfile)
    state_formats = sr_bh_format['StateSection']


data = dict()
for state, mapping in state_formats.items():
    print(state)
    table_mapping = mapping['worksheet table']
    tmp = dict()
    sheet = wb.sheets[state]
    if state != "CA":
        for cat, sheet_cells in table_mapping.items():
            range_location = sheet_cells['range'] # get the range of debit/credits
            range_value = sheet.range(range_location).value
            if isinstance(range_value , (int, float)):
                print("--> converting {} to string".format(range_value))
                range_value = str(range_value * 100) + "%"
            try:
                tmp[cat] = range_value.strip()
            except:
                print("-->", cat, range_location, range_value)
        data[state] = tmp
    sheet.api.Visible = False

data['CA'] = {'Premises': '+/-10%', 'Classification Peculiarities': '+/-25%', 
    'Medical Facilities':  '+/-10%', 'Safety Devices': '+/-10%',
    'Employees-Selection Training, Supervision': '+/-15%', 'Management-Capability/ Cooperation': '+/-15%',
    'Expense of Providing Insurance Services': '+/-5%', 'Other Factors': '+/-10%'
    }

wb.save()
wb.close()

with open("json/SR_QBE_range_values.json", "w") as outfile:
    json.dump(data, outfile)