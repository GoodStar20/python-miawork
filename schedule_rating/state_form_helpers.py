import json
from schedule_rating import models



def workcomp_fieldlist(state, form_type):
    """
    Field names and range values differ by template format
    """
    references = {'QBE': "excel/json/SR_QBE_range_values.json",
        "BH": "excel/json/SR_BH_range_values.json" 
    }

    fname = references[form_type]

    # for now just read off the BH form fields
    with open(fname) as myfile:
        sr_format = json.load(myfile)
        state_format = sr_format[state]
    return state_format # returns {category: category range}


def update_workcomplines(instance_header, states, previous_states=None, form_type=None):
    if previous_states:
        previous_states = set(previous_states)
        current_states = set(states)
        eliminated_states = previous_states.difference(current_states)
        for state in eliminated_states:
            if state == "CA":
                instance_state_header = models.CAHeader.objects.filter(header = instance_header, 
                    state = state, form_type = form_type)
            elif state in ("AZ", "NH", "NM", "OK", "KS", "SD", "VT"):
                instance_state_header = models.AdaptedStateHeader.objects.filter(header = instance_header, 
                    state = state, form_type = form_type)
            else:
                instance_state_header = models.StateHeader.objects.filter(header = instance_header, 
                    state = state, form_type = form_type)
            instance_state_header.delete()
        # current states may include existing states 
        # so we only need to create instances for new states
        current_states.difference_update(previous_states)
        states = list(current_states)

    for state in states:
        # get dictionary of field: field range value
        field_list = workcomp_fieldlist(state, form_type=form_type) # needs to handle CA....
        if state == "AZ":
            state_header = models.AdaptedStateHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type, 
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance = models.AdaptedStateLines(header = state_header, 
                    state = state, category = category, range_available = range_available)
                instance.save()
        if state == "CA":
            state_header = models.CAHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type,
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance = models.CALines(header = state_header, 
                    state = state, category = category, range_available = range_available)
                instance.save()
        elif state in ("NH", "NM", "OK"):
            state_header = models.AdaptedStateHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type,
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance = models.AdaptedStateLines(header = state_header, 
                    state = state, category = category, range_available = range_available)
                instance.save()
        elif state  == 'KS':
            state_header = models.AdaptedStateHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type,
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance = models.AdaptedStateLines(header = state_header, 
                    state = state, category = category, range_available = range_available)
                instance.save()
        elif state in ('SD', 'VT'):
            state_header = models.AdaptedStateHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type, 
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance = models.AdaptedStateLines(header = state_header, 
                    state = state, category = category, range_available = range_available)
                instance.save()
        else:
            state_header = models.StateHeader.objects.create(header = instance_header, 
                state = state, form_type = form_type, 
                carrier = instance_header.carrier, carrier_code=instance_header.carrier_code)
            for category, range_available in field_list.items():
                instance=models.StateLines(header=state_header, state=state, 
                    category=category, range_available = range_available)
                instance.save()
    return 0



states_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 
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
    'WI': 'Wisconsin', 'WY': 'Wyoming', '': '', 'D.C.': 'District of Columbia'}


carrier_info = {'MP': {'carrier': 'Praetorian Insurance - 3501', 'carrier_code': '21172'},
    'WF': {'carrier': 'Praetorian Insurance - 3501', 'carrier_code': '21172'},
    'CP': {'carrier': 'Praetorian Insurance - 3501', 'carrier_code': '21172'},
    'PA': {'carrier': 'Praetorian Insurance - 3501', 'carrier_code': '21172'},
    'CE': {'carrier': 'QBE Insurance Company - 3801', 'carrier_code': '29114'},
    'NI': {'carrier': 'North Pointe Insurance - 3001', 'carrier_code': '35750'}
}
