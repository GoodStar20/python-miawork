import datetime as dt
import decimal

class DataValidator:
    def __init__(self, model):
        self.model = model
        fields = model._meta.get_fields()
        self.field_types = {f.name: f.get_internal_type() for f in fields}

    def validate_date(self, x):
        """
        Prior developer's comment:
        Logic: so when data is read from Excel, if it's a date it should return a datetime Python object.
        For example, if in Excel we have 8/12/2019 --> datetime.datetime(...) should be returned
        Otherwise, it will be returning a string because Python doesn't know wtf it is.
        if it's a string, we'll just replace it with None and leave that field empty
        """      
        if not isinstance(x, dt.datetime):
            # Removed below and replaced changing to None if not a date, 6/11/22
            #x = dt.datetime.strptime('1900-01-01', r'%Y-%m-%d')
            x = None
        return x
        
    def validate_numeric(self, x):
        """
        Basically, just check if the value being read is a float or integer
        """
        if isinstance(x, (float, int, decimal.Decimal)):
            return x

    def review(self, field_name, value):

        # Check date and numeric fields here
        field_type = self.field_types[field_name]

        # Unique Number update to assure no decimal from import
        if field_name == 'unique_number':
            if self.validate_numeric(value):
                return int(value)

         # Check actual renewal model, and if None or '' and field_type dec or int, then set to 0
        if self.model._meta.model_name in ['actualrenewalratechange']:
            if field_type in ('DecimalField', 'IntegerField'):
                if value == None or value == '':
                    return 0
                elif self.validate_numeric(value) == None:
                    return 0
        
        # Check the other date and numeric fields
        if field_type == 'DateField':
            return self.validate_date(value)

        if field_type in ('DecimalField', 'IntegerField'):
            return self.validate_numeric(value)
        
        # Check dropdowns with 'Select' to set to None
        if self.model._meta.model_name in ['loggingheader', 'loggingexposurecategories', 
        'woodmanualheader', 'woodmechanicalcategories', 'mechanicalheader', 'mechanicalcategories']:
            if value == 'Select':
                return None

        # otherwise return the value just as it
        return value

from risk_eval.models import STATE_choices
state_abbreviations = {y:x for x,y in STATE_choices}
state_names = {x:y for x,y in STATE_choices}

def state_name_to_abbreviation(state_name):
    return state_abbreviations.get(state_name, '')

def state_abbreviation_to_name(state_abbreviation):
    return state_names.get(state_abbreviation, '')

