
import os
import xlwings as xl
from time import sleep
import datetime

def get_data_dictionaries_for_loss_history(request):
    hidden = request.POST.getlist('hidden_history')
    policy_period = request.POST.getlist('policy_period')
    effective_date = request.POST.getlist('effective_date')
    no_history = request.POST.getlist('list_exp')
    expiration_date = request.POST.getlist('expiration_date')
    incurred_loss = request.POST.getlist('incurred_loss')
    paid_loss = request.POST.getlist('paid_loss')
    total_claims = request.POST.getlist('total_claims')
    total_indemnity_claims = request.POST.getlist('total_indemnity_claims')
    indemnity_claims = request.POST.getlist('indemnity_claims')
    open_claims = request.POST.getlist('open_claims')
    valuation_date = request.POST.getlist('valuation_date')
    prior_carier = request.POST.getlist('prior_carier')

    loss_history = []
    for count,period in enumerate(policy_period):
        row = {
            'policy period':policy_period[count],
            'effective date':effective_date[count],
            'no_history':hidden[count],
            'expiration_date':expiration_date[count],
            'incurred_loss':incurred_loss[count],
            'paid_loss':paid_loss[count],
            'total_claims':total_claims[count],
            'total_indemnity_claims':total_indemnity_claims[count],
            'indemnity_claims':indemnity_claims[count],
            'open_claims' : open_claims[count],
            'valuation_date' : valuation_date[count],
            'prior_carier' : prior_carier[count]
            }
       
        loss_history.append(row)
    return loss_history    

def get_data_dictionaries_for_large_loss(request):
    doi = request.POST.getlist('doi')
    claimant = request.POST.getlist('claimant')
    status = request.POST.getlist('status')
    litigated = request.POST.getlist('litigated')
    paid = request.POST.getlist('paid')
    incurred = request.POST.getlist('incurred')
    injury_description = request.POST.getlist('injury_description')
    claim_id = request.POST.getlist('claim_id')
    large_loss = []
    for count, name in enumerate(claimant):
        row = {
            'doi':doi[count],
            'claimant':claimant[count],
            'status':status[count],
            'litigated':litigated[count],
            'paid':paid[count],
            'incurred':incurred[count],
            'injury_description':injury_description[count],
            'claim_id' : claim_id[count]
        }
        large_loss.append(row)
    
    return large_loss    

def get_data_dictionaries_for_payroll_premium(request):
    policy_period = request.POST.getlist('payroll_period')
    no_history = request.POST.getlist('payroll_history')
    payroll_premium = request.POST.getlist('payroll_premium')
    payroll_payroll = request.POST.getlist('payroll_payroll')
    hidden = request.POST.getlist('hidden_history')
    
    # for count,period in enumerate(policy_period):
    #     if not count < len(no_history):
    #         no_history.append(False)

    payroll_premium_list = []
    for count,period in enumerate(policy_period):
        row = {
            'policy_period':policy_period[count],
            'no_history': hidden[count],
            'payroll_premium': payroll_premium[count],
            'payroll_payroll' : payroll_payroll[count]
        }
        payroll_premium_list.append(row)
    
    return payroll_premium_list    

# Updated below to just use Ex Mod data for processing
def Risk_Ex_Mod(risk_mode_queryset):

    #policy_period = [query.policy_period for query in acchist_queryset]  
    no_history = [query.no_history for query in risk_mode_queryset]

    ex_mod_value = []
    for query in risk_mode_queryset:
        if query.exmod_val == None:
            exmod_val = ''
        else:
            exmod_val = query.exmod_val    

        ex_mod_value.append(exmod_val)


    # year = []
    # for history in acchist_queryset:
    #     for mode in risk_mode_queryset:
    #         if str(history.expiration_date)[:4] == str(mode.year):
    #             year.append(mode.year)
    
    
    year = [mod.year for mod in risk_mode_queryset]
    risk_mode_list = []
    for count in range(len(no_history)):
        try:
            row = {
                'policy_period': count,
                'no_history':no_history[count],
                'year' : year[count],
                'ex_mod_value':ex_mod_value[count]            
            }
        except Exception as e:
            print(e)
            # row = {
            #     'policy_period':policy_period[count],
            #     'no_history':no_history[count],
            #     'ex_mod_value':ex_mod_value[count]            
            # } 
        risk_mode_list.append(row)

    return risk_mode_list
        
def kill_file(fname,pid):
    app = xl.App()
    pid = pid
    app.quit()
    for i in range(4):
        if os.path.exists(fname):
            try:
                # use sleep to create a gap between quitting the application and removing the application
                sleep(5)
                os.remove(fname) # delete workbook so things don't build up
                os.system("tskill {}".format(pid))
            except:
                os.system("tskill {}".format(pid))

# Compare date of Large Loss vs. effective date to check if within two-year gap
def compareDate(effective_date, coming_date):
    minDate = datetime.date(effective_date.year - 2, effective_date.month, effective_date.day)
    maxDate = datetime.date(effective_date.year, effective_date.month, effective_date.day)
    checkDate = datetime.date(coming_date.year, coming_date.month, coming_date.day)
    
    if(minDate <= checkDate and maxDate > checkDate):
        return True
    return False
    