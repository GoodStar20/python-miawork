"""
import logging
formatter = logging.Formatter('%(asctime)s - %(message)s')
from risk_eval import forms

from excel import handle_uploaded_file, Upload
#test_upload("BH", "C:/Users/jnavarrete/Documents/Midwestern Insurance Agency/REPORTS/RISK EVALUATION 2020 RENEWAL - BH Q1 15346.xlsm")
#test_upload("BH", "C:/Users/jnavarrete/Documents/Midwestern Insurance Agency/REPORTS/Risk Eval Act BH13847.xlsm")


def create_logger():
    # logging parameters #
    file_handler = logging.FileHandler("tmp/test_upload.log")
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

class ReadWB:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = open(file_path, "rb")
    
    def chunks(self):
        chunksize = 1000
        while True:
            chunk = self.data.read(chunksize)
            if not chunk:
                break # done
            yield chunk

def test_upload(form_type, file_path):

    #form_type: BH or QBE

    logger = create_logger()
    logger.info("form is valid")
    workbook = ReadWB(file_path)
    logger.info("Reading: {}".format(file_path))
    fname = handle_uploaded_file(workbook)
    # check form types to determine which module to use
    uploader = Upload(fname = fname, user_id = 1, 
        upload_id = None, kind=form_type)
    logger.info("Uploader initiated")
    # in case there is an issue uploading the data
    # TO DO LIST:
    # there needs to be a way to determine what (if any) data was uploaded
    app = uploader.open_workbook()
    pid = app.pid
    logger.info("App: {} with PID: {}".format(app, pid))
    try:
        logger.info("Uploading data from workbook")
        uploader.risk_eval() # run all for Risk Eval
        logger.info("Risk Eval Section Complete")
        uploader.uw_specialty() # UW Specialty Notes
        logger.info("UW Specialty Section Complete")
        uploader.exit() # close and delete tmp workbook
        logger.info("Closing workbook")
        pk = uploader.generalinfo.pk
        return True
    except:
        uploader.logger.error("Issue has occured!!", exc_info=True)
        uploader.exit()
        try:
            os.kill(pid)
        except:
            pass
        logger.error("Could not read Risk Eval form!")
        return False
    return True
"""