import yearfrac as yf
from risk_eval import models
from math import floor
from pprint import pprint
from django.db.models import Avg, Count, Min, Sum

def date_factor(d1, d2):
    num = yf.yearfrac(d1, d2)
    return floor(num*12)

def handle_calculation_loss_rating(acchist_queryset, loss_queryset)->dict:
    
    loss_list = []
    lass_age_value = 0
    try:
        for i in range(len(loss_queryset)):
            d1 = loss_queryset[i].__dict__['valuation_date']
            d2 = acchist_queryset[i].__dict__['effective_date']
            loss_dic = loss_queryset[i].__dict__

            if not d1:
                d1 = d2
                loss_dic['age'] = lass_age_value
                loss_dic['valuation_date'] = d2
                
            else:
                loss_dic['age'] = date_factor(d2, d1)
            
            lass_age_value = loss_dic['age']

            loss_list.append(loss_dic)
    except:
        pass
    return loss_list

def temp(pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk = pk)
    acchist_queryset = models.AccountHistory.objects.filter(generalinfo = instance_generalinfo).order_by('policy_period')
    loss_queryset = models.LossRatingValuation.objects.filter(generalinfo = instance_generalinfo).order_by('policy_period')
    return handle_calculation_loss_rating(acchist_queryset, loss_queryset)

def queryset_for_BH(pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk = pk)
    acchist_queryset = models.AccountHistory.objects.filter(generalinfo = instance_generalinfo).order_by('policy_period')
    loss_queryset = models.LossRatingValuation.objects.filter(generalinfo = instance_generalinfo).order_by('policy_period')
    
    return handle_calculation_loss_rating(acchist_queryset, loss_queryset)

def calculate_total_for_BH(queryset):
    age_total = sum([item['age'] for item in queryset])
    industry_ldf_total = sum([int(item['industry_ldf'] or 0) for item in queryset])
    trended_payroll_total = sum([int(item['trended_payroll'] or 0) for item in queryset])
    ultimate_reported_claims_total = sum([int(item['ultimate_reported_claims'] or 0) for item in queryset])
    ultimate_indemnity_claims_total = sum([int(item['ultimate_indemnity_claims'] or 0) for item in queryset])
    payroll_total = sum([int(item['payroll'] or 0) for item in queryset])
    prior_carrier_total = sum([int(item['prior_carrier'] or 0) for item in queryset])
    bh_developed_loss_ratio_total =  sum([int(item['developed_losses'] or 0) for item in queryset])

    return age_total, industry_ldf_total, trended_payroll_total, ultimate_reported_claims_total, ultimate_indemnity_claims_total, payroll_total, prior_carrier_total, bh_developed_loss_ratio_total

def calculate_total(queryset): 
    age_total = sum([item['age'] for item in queryset])
    developed_losses_total = sum([int(item['developed_losses'] or 0) for item in queryset])
    bf_losses_total = sum([int(item['bf_losses'] or 0) for item in queryset])
    selected_ult_losses_total = sum([int(item['selected_ult_losses'] or 0) for item in queryset])
    loss_trend_factor_total = sum([int(item['loss_trend_factor'] or 0) for item in queryset])
    ult_trended_losses_total = sum([int(item['ult_trended_losses'] or 0) for item in queryset])
    payroll_total = sum([int(item['payroll'] or 0) for item in queryset])
    qbe_developed_loss_ratio_total = sum([int(item['qbe_developed_loss_ratio'] or 0) for item in queryset])
    
    return age_total, developed_losses_total, bf_losses_total, selected_ult_losses_total,loss_trend_factor_total, ult_trended_losses_total, payroll_total, qbe_developed_loss_ratio_total

def calculate_average_all_year(queryset):
    age_average_all_year = sum([item['age'] for item in queryset]) / len([item['age'] for item in queryset])
    developed_losses_average_all_year = sum([int(item['developed_losses'] or 0) for item in queryset]) / len([item['developed_losses'] for item in queryset])
    bf_losses_average_all_year = sum([int(item['bf_losses'] or 0) for item in queryset])/ len([item['bf_losses'] for item in queryset])
    selected_ult_losses_average_all_year = sum([int(item['selected_ult_losses'] or 0) for item in queryset]) / len([item['selected_ult_losses'] for item in queryset])
    loss_trend_factor_average_all_year = sum([int(item['loss_trend_factor'] or 0) for item in queryset]) / len([item['loss_trend_factor'] for item in queryset])
    ult_trended_losses_average_all_year = sum([int(item['ult_trended_losses'] or 0) for item in queryset]) / len([item['ult_trended_losses'] for item in queryset])
    payroll_average_all_year = sum([int(item['payroll'] or 0) for item in queryset]) / len([item['payroll'] for item in queryset])
    qbe_developed_loss_ratio_average_all_year = sum([int(item['qbe_developed_loss_ratio'] or 0) for item in queryset]) / len([item['qbe_developed_loss_ratio'] for item in queryset])

    return age_average_all_year, developed_losses_average_all_year, bf_losses_average_all_year, selected_ult_losses_average_all_year, loss_trend_factor_average_all_year, ult_trended_losses_average_all_year, payroll_average_all_year, qbe_developed_loss_ratio_average_all_year

def calculate_average_3_year(queryset):
    age_average_3_year = sum([item['age'] for item in queryset][:3]) / len([item['age'] for item in queryset][:3])
    developed_losses_average_3_year = sum([int(item['developed_losses'] or 0) for item in queryset][:3]) / len([item['developed_losses'] for item in queryset][:3])
    bf_losses_average_3_year = sum([int(item['bf_losses'] or 0) for item in queryset][:3])/ len([item['bf_losses'] for item in queryset][:3])
    selected_ult_losses_average_3_year = sum([int(item['selected_ult_losses'] or 0) for item in queryset][:3]) / len([item['selected_ult_losses'] for item in queryset][:3])
    loss_trend_factor_average_3_year = sum([int(item['loss_trend_factor'] or 0) for item in queryset][:3]) / len([item['loss_trend_factor'] for item in queryset][:3])
    ult_trended_losses_average_3_year = sum([int(item['ult_trended_losses'] or 0) for item in queryset][:3]) / len([item['ult_trended_losses'] for item in queryset][:3])
    payroll_average_3_year = sum([int(item['payroll'] or 0) for item in queryset][:3]) / len([item['payroll'] for item in queryset][:3])
    qbe_developed_loss_ratio_average_3_year = sum([int(item['qbe_developed_loss_ratio'] or 0) for item in queryset][:3]) / len([item['qbe_developed_loss_ratio'] for item in queryset][:3])

    return age_average_3_year, developed_losses_average_3_year, bf_losses_average_3_year, selected_ult_losses_average_3_year, loss_trend_factor_average_3_year, ult_trended_losses_average_3_year, payroll_average_3_year, qbe_developed_loss_ratio_average_3_year