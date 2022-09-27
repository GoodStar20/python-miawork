from django.forms import ModelForm, inlineformset_factory, Textarea, SelectDateWidget
from schedule_rating import models
from django import forms


MONTHS = {
    1:'01', 2:'02', 3:'03', 4:'04',
    5:'05', 6:'06', 7:'07', 8:'08',
    9:'09', 10:'10', 11:'11', 12:'12'
}

"""
Home List View Filter Form 
"""
def get_uw_choices():
    choices = set((x.uw, x.uw) for x in FilterListView.UW_choices)
    choices = list(choices)
    choices.append(('', '--All--'))
    
    return (x for x in choices)

class FilterListView(forms.Form):
    UW_choices = models.SRHeader.objects.all().order_by('uw')

    field_choices = [('id', 'ID'), ('user', 'User'), ('last_modified_date', 'Last Modified Date'), ('created_date', 'Created Date'),
                     ('dba','DBA'), ('uw', 'UW'), ('term', 'Term'), ('usub', 'USub'), 
                     ('agent_number', 'Agent Number'), ('effective_date', 'Effective Date'), 
                     ('expiration_date', 'Expiration Date'), ('policy_number', 'Policy Number'),
                     ('data_set','Data Set'), ('account_number','Account Number'), 
                     ('date_prepared', 'Date Prepared'), ('quote_number', 'Quote Number'), 
                     ('', '')]

    form_id = forms.IntegerField(required=False, label='Form ID')
    unique_number = forms.IntegerField(required=False, label='Unique Number', help_text = "Enter the Risk Eval Unique Number if you know the form you're searching for")
    uw = forms.ChoiceField(choices=get_uw_choices, required=False, initial='', label = 'Underwriter')
    order_by = forms.ChoiceField(choices=field_choices, required=False, label = 'Order by')
    order = forms.ChoiceField(
        choices=[('', 'ascending'), ('-', 'descending')], required=False, label='Order')
    results = forms.ChoiceField(choices = [(5, 5), (10, 10), (15, 15), (20, 20)], required=False)

"""
Entry Page 1
"""

class CreateSRHeaderForm(ModelForm):
    class Meta:
        model = models.SRHeader
        fields = ['form_type', 'named_insured','dba', 'uw', 'term','unique_number','agent_number','effective_date',
            'expiration_date','policy_number','data_set','account_number','date_prepared','quote_number']
        widgets = {
            "effective_date": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
            "expiration_date": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
            "date_prepared": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
        }

class EditSRHeaderForm(ModelForm):
    class Meta:
        model = models.SRHeader
        fields = ['named_insured','dba', 'uw', 'term','unique_number','agent_number','effective_date',
            'expiration_date','policy_number','data_set','account_number','date_prepared','quote_number']
        widgets = {
            "effective_date": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
            "expiration_date": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
            "date_prepared": SelectDateWidget(years = list (range(1990, 2030)), months = MONTHS),
        }

"""
Select States (Multiple Choice)
"""
class SelectStatesForm(ModelForm):
    class Meta:
        model = models.SRStates
        fields = ['states']

"""
Entry Page 2
"""
class StateHeaderForm(ModelForm):
    class Meta:
        model= models.StateHeader
        fields = ['risk_location', 'effective_date']
        widgets = {'effective_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
        }
    
from django.forms import modelformset_factory

StateFormset = modelformset_factory(model = models.StateLines, 
    fields = ['category', 'range_available', 
        'credit_applied','debit_applied','reason_basis'], 
    extra=0)

# Arizona #
class AZHeaderForm(ModelForm):
    class Meta:
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'status', 
            'loss_prevention_survey', 'loss_prevention_survey_date', 
            'ncci_rates', 'rating_eligibility', 'az_sr_plan_2']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
            }

AZLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 
        'previous_credit_applied', 'previous_debit_applied',
        'credit_applied','debit_applied','reason_basis'], extra=0)

## California ##
class CAHeaderForm(ModelForm):
    class Meta: 
        model = models.CAHeader
        fields = ['risk_location', 'effective_date']
        widgets = {'effective_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

CALineFormset = modelformset_factory(model = models.CALines, 
    fields = ['category', 'range_available', 'below_average', 'average', 
            'superior', 'reason_basis'], extra=0)

## Kansas ##
# uses AdaptedStateHeader
class KSHeaderForm(ModelForm):
    class Meta: 
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'effective_date', 'standard_premium']
        widgets = {'effective_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
            }

KSLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'credit_applied', 
        'debit_applied','reason_basis'], extra=0)

## New Hampshire ##
# uses AdaptedStateHeader
class NHHeaderForm(ModelForm):
    class Meta: 
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'loss_prevention_survey', 
            'loss_prevention_survey_date', 'standard_premium', 'rating_eligibility']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

NHLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'credit_applied', 
        'debit_applied','reason_basis'], extra=0)

## New Mexico ##
# uses AdaptedStateHeader
class NMHeaderForm(ModelForm):
    class Meta: 
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'status',
            'loss_prevention_survey', 'loss_prevention_survey_date', 
            'rating_eligibility', 'standard_premium']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

NMLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'previous_credit_applied', 'previous_debit_applied',
        'credit_applied', 'debit_applied', 'reason_basis'], extra=0)

## South Dakota ##
# uses AdaptedStateHeader
class SDHeaderForm(ModelForm):
    class Meta: 
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'status', 'loss_survey_format',
            #'loss_prevention_survey', 
            'loss_prevention_survey_date', 
            'standard_premium_exists', 'standard_premium']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

SDLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'previous_credit_applied', 'previous_debit_applied', 'credit_applied', 
        'debit_applied','reason_basis'], extra=0)

## Vermont ##
# uses AdaptedStateHeader
class VTHeaderForm(ModelForm):
    class Meta: 
        model = models.AdaptedStateHeader
        fields = ['risk_location', 'risk_id', 'status', 
            'loss_prevention_survey', 'loss_prevention_survey_date', 
            'standard_premium_exists', 'standard_premium']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

VTLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'credit_applied', 
        'debit_applied','reason_basis'], extra=0)

class AdaptedStateHeaderForm(ModelForm):
    class Meta:
        model = models.AdaptedStateHeader
        fields = ['status', 'risk_location', 'risk_id', 
            'loss_prevention_survey', 'loss_prevention_survey_date',
            'standard_premium']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

LinesV3Formset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'credit_applied', 
        'debit_applied', 'reason_basis'], extra=0)

## Oklahoma ## 
class OKHeaderForm(ModelForm):
    class Meta:
        model = models.AdaptedStateHeader
        fields = ['status', 'risk_location', 'risk_id', 
            'loss_prevention_survey', 'loss_prevention_survey_date',
            'wcpr_credits', 'merit_plan_debits', 'merit_plan_credits']
        widgets = {'loss_prevention_survey_date': SelectDateWidget(years=range(1985, 2030), months = MONTHS),
                   }

OKLineFormset = modelformset_factory(model = models.AdaptedStateLines, 
    fields = ['category', 'range_available', 'previous_credit_applied', 
        'previous_debit_applied', 'credit_applied', 'debit_applied', 
        'reason_basis'], extra=0)

"""
Form to upload workbook
"""

class UploadFileForm(ModelForm):
    file = forms.FileField(label='Select a Schedule Rating Form')

    class Meta:
        model = models.Upload
        fields = '__all__'


"""
Form to export data to workbooks
"""

class ExportFormSR(ModelForm):
    class Meta:
        model = models.Export
        fields = ['comments', 'export_to_webdocs']

