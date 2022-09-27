from fileinput import filename
import os
from urllib import response
import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workcomp.settings")
django.setup()

from excel import Upload
from risk_eval import models
import pandas as pd
import time
import datetime as dt
#import logging

#logging.basicConfig(filename = "test.log", format = "%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

df = pd.read_csv("E:/TEST.csv")
#df = df.loc[351:360]
print(df.head())

results = []
start = dt.datetime.now()
print("Start: {}".format(start))


with open("E:/Test/bulk_upload_progress.csv", "a+") as myfile:
    myfile.write("#,fname,form-type,upload_instance,generalinfo_id,complete\n")
    for i, row in df.iterrows():
       
        # Original was PC PATH (with a space)
        # fname = row['PC PATH']

        # When moved to database used "_" between PC and PATH
        fname = row['PC_PATH']

        # Check if Excel is BH or QBE
        if row['DATASET'] == "BH":
            form_type = "BH"
        else:
            form_type = "QBE"        

        if os.path.exists(fname.strip()) and 'xlsm' in fname:
            upload_instance = models.Upload(form_type = form_type, created_by = 1)
            upload_instance.save()
           
            uploader = Upload(fname=fname, user_id=1, 
                upload_id=upload_instance.id, kind=form_type, cleanup=False)
            
            try:
                # start app
                app = uploader.open_workbook()
                pid = app.pid

                try:
                    # Removing below as it doesn't appear to be required for Create approach, 3/30/22
                    #response, unique_number, general_infos = uploader.check_general_info_exists()
                    response = "Create"
                    unique_number = None

                    uploader.risk_eval(response, unique_number, form_type, '') # run all for Risk Eval
                    uploader.uw_specialty(response, unique_number, '') # UW Specialty Notes
                    uploader.exit() # close and delete tmp workbook

                    # check to make sure the Excel workbook is closed
                    os.system("tskill {}".format(pid))
                    output = (i, fname, form_type, upload_instance.id, uploader.generalinfo.id, True)
                    print("Successfully uploaded: ", output)
                except:
                    uploader.logger.error("Upload was terminated.", exc_info=True)
                    uploader.exit()
                    # If for some reason the export becomes unresponsive
                    # Kill the process
                    os.system("tskill {}".format(pid))
                    output = (i, fname, form_type, upload_instance.id, uploader.generalinfo.id, False)
                    print("Error with ", output)
                
                results.append(output)
                line = ",".join([str(x) for x in output]) + "\n"
                myfile.write(line)

                # Let the system rest to not overload it
                # Lowered to 1 from original of 3, to help run faster
                time.sleep(1)
            except:
                output = (i, fname, form_type, upload_instance.id, None, False)
                print("Error with(first)", output)
                results.append(output)
                line = ",".join([str(x) for x in output]) + "\n"
                myfile.write(line)
                pass

output_df = pd.DataFrame(data = results, columns = ['#', 'fname', 'form_type', 'upload_instance', 'generalinfo_id', 'complete'])
output_df.to_csv("E:/Test/bulk_upload.csv", index=False)

end = dt.datetime.now()
print("End: {}".format(end))
print("Duration: {}".format(end-start))
quit()