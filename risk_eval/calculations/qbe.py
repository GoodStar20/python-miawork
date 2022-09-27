from risk_eval import models


def renewal_target_rate_increase(instance):
    try:
        renewal_target_rate_increase = float(instance.segment_target_increase + instance.loss_history_modification + instance.exposure_modification)
    
    except:
        renewal_target_rate_increase = None
    
    return renewal_target_rate_increase

def actual_renewal_rate_increase(instance):
    try:
        ren_adj_rate = float(instance.ren_rate * instance.ren_cr_db)
    except:
        ren_adj_rate = None

    try:
        exp_adj_rate = float(instance.exp_rate * instance.exp_cr_db)
    except:
        exp_adj_rate = None

    try:        
        actual_renewal_rate_increase = round((ren_adj_rate/exp_adj_rate -1) * 100,1) 
    except:
        actual_renewal_rate_increase = None

    return actual_renewal_rate_increase, ren_adj_rate, exp_adj_rate