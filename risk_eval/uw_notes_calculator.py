def calculate_score(query, reference):
        print('-------------------------')
        print(reference)
        print('-------------------------')

        data = query.__dict__
        scores = []
        #n = len(list(reference.keys()))
        for field, grade in data.items():
                try:
                        val = reference[field][grade]
                        scores.append(val)
                except:
                        pass
        n = len(scores)
        
        if n == 0:
                avg_score = 0
        else:
                avg_score = round(sum(scores) / n, 1)
        
        return avg_score




wood_manual_ref = {
    'operations_housekeeping': {
                'Select': 0,
                'FAA Superior housekeeping program, enforced by management': 4,
                'AA Housekeeiping program in place. Clean workspace': 3,
                'A Housekeeping program in place. Some accumulation': 2,
                'BA No formal housekeeping program.': 1
			},
    'forklift_usage': {
            'Select': 0,
            'FAA Training in place, no losses in past 3 years': 4, 
            'AA Training in place, minor losses in past 3 years': 3, 
            'A No training or losses in past 3 years': 2, 
            'BA No training and losses in past 3 years': 1
            },
    'losses_past_3yrs': {
            'Select': 0,
            'FAA No Losses': 3, 
            'AA Loss ratio < 30% w/o auto related WC claims': 2, 
            'A Loss ratio < 50% or related WC claims': 0, 
            'BA Loss ratio > 50% or claims from uninsured subs': 1
            },
    'business_experience': {
            'Select': 0,
            'FAA >10 years continuous in industry': 4, 
            'AA 6 to 10 years continuous in industry': 3, 
            'A 3 to 5 years continuous in industry': 2, 
            'BA <3 years continuous in industry': 1
            },
    'cdl_auto_exposure': {
            'Select': 0,
            'FAA No exposure or 100% insured subcontractors': 4, 
            'AA Owned autos insurred and subcontractors': 3,
            'A 100% owned autos': 2, 
            'BA Any use of uninsured subcontractors': 1
            },
    'owned_auto_driver_experience': {
            'Select': 0,
            'FAA 75% CDL 5 years experience': 4, 
            'AA 60% of CDL 5 years experience': 3, 
            'A 40% of CDL 5 years experience': 2, 
            'BA <40% of CDL 5 years experience': 1
            },
    'owned_auto_mvr': {
            'Select': 0,
            'FAA 60% CDL clear <10% borderline': 4, 
            'AA 50% to 59% CDL clear <10% borderline': 3, 
            'A 40% to 49% CDL clear <10% borderline': 2, 
            'BA <40% CDL clear and / or >10% borderline': 1
            },
    'safety': {
            'Select': 0,
            'FAA very proactive, anticipates hazards and formal plan in place': 4, 
            'AA Established policies in plance and active management': 3, 
            'A Aware of major exposures and information plan in place': 2, 
            'BA Management not actively involved and no plan': 1
            },
    'loss_handling_and_trends': {
            'Select': 0,
            'FAA Management has influence and loss results reflect': 4, 
            'AA Management taking action, review of losses': 3, 
            'A Management addresses on a reactive basis': 2, 
            'BA Management casually aware, ineffective approach': 1
            },
    'employee_turnover': {
            'Select': 0,
            'FAA low turnover, stable, experienced <10%': 4, 
            'AA low turnover, stable, experience <15%': 3, 
            'A average turnover up to 20%': 2, 
            'BA below average turnover >20% turnover rate': 1
            },
    'subcontracting': {
            'Select': 0,
            'FAA no exposure': 4, 
            'AA written program with exposure': 3, 
            'A no program, requires certificate of insurance': 2,
            'BA no program with uninsured subcontractors': 1
            },
#     'financial': { 'Not included at this time': 0
#             }
}
    
mechanical_ref = {
    'cutting_operations': {
            'Select':0,
            'FAA Optimizing saws, mechanical sorting, lock out tag out': 4,
            'AA Mechanical sorting, guards, lock out tag out enforced': 3, 
            'A Partially mechanical sorting, Log out tag out, guards': 2, 
            'BA All manual sorting, informal lock out tag out': 1
             },
    'dust_collection': {
            'Select':0,
            'FAA Dust Collection system, superior housekeeping': 4,
            'FAA Dust Collection system, superior housekeeping': 3,
            'AA Superior housekeeping, management enforces': 2,
            'A Housekeeping program in place': 1,
            'BA No dust collection or housekeeping program':0
            },
    'forklift_usage': {
            'Select':0,
            'FAA Training in place, no losses in past 3 years': 4, 
            'AA Training in place, minor losses in past 3 years': 3, 
            'A No training or losses in past 3 years': 2, 
            'BA No training and losses in past 3 years': 1
            },
    'losses_past_3yrs': {
            'Select':0,
            'FAA No Losses': 3, 
            'AA Loss ratio < 30% w/o auto related WC claims': 2, 
            'A Loss ratio < 50% or related WC claims': 0, 
            'BA Loss ratio > 50% or claims from uninsured subs': 1
            },
    'business_experience': {
            'Select':0,
            'FAA >10 years continuous in industry': 4, 
            'AA 6 to 10 years continuous in industry': 3, 
            'A 3 to 5 years continuous in industry': 2, 
            'BA <3 years continuous in industry': 1
            },
    'cdl_auto_exposure': {
            'Select':0,
            'FAA No exposure or 100% insured subcontractors': 4, 
            'AA Owned autos insurred and subcontractors': 3,
            'A 100% owned autos': 2, 
            'BA Any use of uninsured subcontractors': 1
            },
    'owned_auto_driver_experience': {
            'Select':0,
            'FAA 75% CDL 5 years experience': 4, 
            'AA 60% of CDL 5 years experience': 3, 
            'A 40% of CDL 5 years experience': 2, 
            'BA <40% of CDL 5 years experience': 1
            },
    'owned_auto_mvr': {
            'Select':0,
            'FAA 60% CDL clear <10% borderline': 4, 
            'AA 50% to 59% CDL clear <10% borderline': 3, 
            'A 40% to 49% CDL clear <10% borderline': 2, 
            'BA <40% CDL clear and / or >10% borderline': 1
            },
    'safety': {
            'Select':0,
            'FAA very proactive, anticipates hazards and formal plan in place': 4, 
            'AA Established policies in plance and active management': 3, 
            'A Aware of major exposures and information plan in place': 2, 
            'BA Management not actively involved and no plan': 1
            },
    'loss_handling_and_trends': {
            'Select':0,
            'FAA Management has influence and loss results reflect': 4, 
            'AA Management taking action, review of losses': 3, 
            'A Management addresses on a reactive basis': 2, 
            'BA Management casually aware, ineffective approach': 1
            },
    'employee_turnover': {
            'Select':0,
            'FAA low turnover, stable, experienced <10%': 4, 
            'AA low turnover, stable, experience <15%': 3, 
            'A average turnover up to 20%': 2, 
            'BA below average turnover >20% turnover rate': 1
            },
    'subcontracting': {
            'Select':0,
            'FAA no exposure': 4, 
            'AA written program with exposure': 3, 
            'A no program, requires certificate of insurance': 2,
            'BA no program with uninsured subcontractors': 1
            },
#     'financial': { 'Not included at this time': 0
#             }
}


logging_ref = {
    'general_operations': {
                'Select':0,
                'FAA > 95% mechanized, machine delimbing': 4, 
		'AA > 90% mechanized, pull thru delimbing':3, 
		'A > 80% mechanized, manual trimming': 2, 
		'BA < 80% mechanized, maunal trimming':1,
		},
    'terrain': {
        'Select':0,
        'FAA Flat or 1st or 2nd thinning operation': 4,
        'AA Flat or clear cut operations': 3,
        'A Flat to rolling > 75% soft wood cutting': 2,
        'BA Hilly with hardwood cutting': 1
        },
    'losses_past_3yrs': {
            'Select':0,
            'FAA No Losses': 3, 
            'AA Loss ratio < 30% w/o auto related WC claims': 2, 
            'A Loss ratio < 50% or related WC claims': 0, 
            'BA Loss ratio > 50% or claims from uninsured subs': 1
            },
    'business_experience': {
            'Select':0,
            'FAA >10 years continuous in industry': 4, 
            'AA 6 to 10 years continuous in industry': 3, 
            'A 3 to 5 years continuous in industry': 2, 
            'BA <3 years continuous in industry': 1
            },
    'log_hauling_auto': {
            'Select':0,
            'FAA No exposure or 100% insured subcontractors': 4,
            'AA Owned autos insured and subcontractors': 3,
            'A 100% owned autos': 2,
            'BA Any use of uninsured subcontractors': 1
            },
    'owned_auto_driver_experience': {
            'Select':0,
            'FAA 75% CDL 5 years experience': 4, 
            'AA 60% of CDL 5 years experience': 3, 
            'A 40% of CDL 5 years experience': 2, 
            'BA <40% of CDL 5 years experience': 1
            },
    'owned_auto_mvr': {
            'Select':0,
            'FAA 60% CDL clear <10% borderline': 4, 
            'AA 50% to 59% CDL clear <10% borderline': 3, 
            'A 40% to 49% CDL clear <10% borderline': 2, 
            'BA <40% CDL clear and / or >10% borderline': 1
            },
    'safety': {
            'Select':0,
            'FAA very proactive, anticipates hazards and formal plan in place': 4, 
            'AA Established policies in plance and active management': 3, 
            'A Aware of major exposures and information plan in place': 2, 
            'BA Management not actively involved and no plan': 1
            },
    'loss_handling_and_trends': {
            'Select':0,
            'FAA Management has influence and loss results reflect': 4, 
            'AA Management taking action, review of losses': 3, 
            'A Management addresses on a reactive basis': 2, 
            'BA Management casually aware, ineffective approach': 1
            },
    'employee_turnover': {
            'Select':0,
            'FAA low turnover, stable, experienced <10%': 4, 
            'AA low turnover, stable, experience <15%': 3, 
            'A average turnover up to 20%': 2, 
            'BA below average turnover >20% turnover rate': 1
            },
    'subcontracting': {
            'Select':0,
            'FAA no exposure': 4, 
            'AA written program with exposure': 3, 
            'A no program, requires certificate of insurance': 2,
            'BA no program with uninsured subcontractors': 1
            },
#     'financial': { 'Not included at this time': 0
#             }

}
    
    