from django.forms import ModelForm, fields, inlineformset_factory, Textarea, SelectDateWidget, CharField
from . import models
from django import forms


MONTHS = {
    1: '01', 2: '02', 3: '03', 4: '04',
    5: '05', 6: '06', 7: '07', 8: '08',
    9: '09', 10: '10', 11: '11', 12: '12'
}

start_year = 2010

"""
List View Filter Form
"""

def get_uw_choices():
    choices = set((x.uw, x.uw) for x in FilterListView.UW_choices)
    choices = list(choices)
    choices.append(('', '--All--'))
    choices.sort()
    return (x for x in choices)

class FilterListView(forms.Form):
    UW_choices = models.GeneralInfo.objects.all().order_by('uw')

    field_choices = [('', ''), ('id', 'ID'), ('last_modified_date', 'Last Modified Date'), ('created_date', 'Created Date'),
                     ('named_insured', 'Name Insured'), ('dba',
                                                         'DBA'), ('uw', 'UW'),
                     ('effective_date', 'Effective Date'),
                     ('agent_number', 'Agent Number'),
                     ('unique_number', 'Unique Number'), ('account_number',
                                                          'Account Number')]

    form_id = forms.IntegerField(required=False, label='Form ID',
                                 help_text="Enter the form ID if you know the form you're searching for")
    unique_number = forms.IntegerField(required=False, label='Unique Number',
                                       help_text="Enter the Risk Eval Unique Number if you know the form you're searching for")
    uw = forms.ChoiceField(choices=get_uw_choices,
                           required=False, initial='', label='Underwriter')
    order_by = forms.ChoiceField(
        choices=field_choices, required=False, label='Order by')
    order = forms.ChoiceField(
        choices=[('', 'ascending'), ('-', 'descending')], required=False, label='Order')
    results = forms.ChoiceField(
        choices=[(5, 5), (10, 10), (15, 15), (20, 20)], required=False)

"""
Risk Eval Review Form
# this form will be used to review warnings for each section of the Risk Eval
"""

class ReviewRiskForm(forms.Form):
    field_choices = [('GeneralInfo', 'Section A - General Info'),
                     ('GeneralInfoPremium', 'Section A - Premium'),
                     ('AccountHistory', 'Section B - Account History'),
                     ('LossRatingValuation', 'Section B - Loss Rating'),
                     ('RiskHeader', 'Section C - Risk Header'), ('RiskExmod',
                                                                 'Section C - Risk Exmod'),
                     ('Checklist', 'Section D'),
                     ('Comments', 'Section F'),
                     ('Claims', 'Section G - Claims'), ('EvalUnderwriter',
                                                        'Section G - Underwriter'),
                     ('Notes', 'Section H')]
    section = forms.ChoiceField(
        choices=field_choices, label='Choose a Section', initial='Section A - General Info')

"""
Section A General Information
"""

class CreateRiskEvalForm(ModelForm):
    class Meta:
        months = {
            1: '1', 2: '2', 3: '3', 4: '4',
            5: '5', 6: '6', 7: '7', 8: '8',
            9: '9', 10: '10', 11: '11', 12: '12'
        }
        model = models.GeneralInfo
        fields = ['carrier', 'unique_number', 'uw', 'named_insured', 'effective_date', 'business_overview',
                  'expiration_date', 'term', 'state', 'agent_number', 'agency_name', 'quote_number',
                  'unique_number', 'account_number', 'data_set']
        widgets = {
            "business_overview": Textarea(attrs={'rows': 3, 'cols': 30}),
            # "effective_date": SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
            # "expiration_date": SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
        }

class EditFormGeneralInfo(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projected_net_premium'].widget.attrs.update(
            {'placeholder': 'Estimated Net Premium'})
        self.fields['projected_base_premium'].widget.attrs.update(
            {'placeholder': 'Manual Premium', 'disabled': 'True'})

    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.GeneralInfo
        fields = ['carrier', 'named_insured', 'uw', 'dba', 'business_overview', 'effective_date', 'expiration_date', 'term', 'state', 'agent_number', 'agency_name', 'quote_number',
                  'unique_number', 'account_number', 'data_set', 'number_employees', 'projected_payroll', 'term_frequency', 'projected_base_premium', 'projected_net_premium', 'governing_class_code']
        widgets = {
            "business_overview": Textarea(attrs={'rows': 3, 'cols': 30}),
            # "effective_date": SelectDateWidget(years=list(range(start_year, 2030)), months=MONTHS),
            # "expiration_date": SelectDateWidget(years=list(range(start_year, 2030)), months=MONTHS),
        }

class FormGeneralInfoPremium(ModelForm):
    class Meta:
        model = models.GeneralInfoPremium
        fields = ('state', 'class_code', 'manual_premium')

PremiumLineFormSet = inlineformset_factory(models.GeneralInfo, models.GeneralInfoPremium, fields=(
    'state', 'class_code', 'manual_premium'), form=FormGeneralInfoPremium, max_num=51, extra=10)

"""
Section B Account History and Loss Rating
"""

class AcctHistoryForm(ModelForm):
    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.AccountHistory
        fields = ['policy_period', 'effective_date', 'expiration_date', 'written_premium', 'incurred_losses',
                  'paid_losses', 'total_claims', 'total_indemnity_claims', 'indemnity_claims', 'open_claims', 'no_history']
        widgets = {'effective_date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
                   'expiration_date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
                   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['policy_period'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['effective_date'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 80%'})
        self.fields['expiration_date'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 80%'})
        self.fields['written_premium'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['incurred_losses'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['paid_losses'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['total_indemnity_claims'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['indemnity_claims'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['total_claims'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})
        self.fields['open_claims'].widget.attrs.update(
            {'class': 'form-control', 'style': 'width: 40%'})

AccountFormSet = forms.modelformset_factory(form=AcctHistoryForm, model=models.AccountHistory,
                                            min_num=0, max_num=5, extra=0)

class LossRatingForm(ModelForm):
    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.LossRatingValuation
        fields = ['policy_period',
                  'valuation_date', 'payroll', 'prior_carrier', 'no_history']
        widgets = {'valuation_date': SelectDateWidget(
            years=range(start_year, 2030), months=MONTHS), }

LossFormSet = forms.modelformset_factory(form=LossRatingForm, model=models.LossRatingValuation,
                                         min_num=0, max_num=5, extra=0)

class LossHistoryForm(ModelForm):
    prior_carrier = forms.CharField(required=False)
    validation = forms.DateField(required=False)

    class Meta:
        model = models.AccountHistory
        fields = ['policy_period', 'no_history', 'effective_date', 'expiration_date', 'incurred_losses',
                  'paid_losses', 'total_claims', 'total_indemnity_claims', 'indemnity_claims', 'open_claims', 'prior_carrier', 'validation']


LossHistoryFormset = forms.modelformset_factory(
    form=LossHistoryForm, model=models.AccountHistory)

"""
C. Risk Characteristics
"""

class RiskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs.update(
            {'placeholder': 'Enter Financial Score'})

    class Meta:
        model = models.RiskHeader
        fields = ['group_med', 'active_injury_program', 'return_to_work_program', 'loss_free_safety_incentive',
                  'safety_meetings', 'financial_indicators', 'score', 'management_attitude', 'exposures']
        #fields = '__all__'


RiskExmodFormSet = inlineformset_factory(parent_model=models.GeneralInfo, model=models.RiskExmod, fields=[
                                         'year', 'exmod_val', 'no_history'], min_num=6, max_num=6, extra=6,
                                         can_delete=False)

"""
D. Checklist
"""

class ChecklistForm(ModelForm):
    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.Checklist
        fields = ['date_signed_wc_acord130', 'supplemental_application', 'supplemental_application_year',
                  'loss_control_report', 'prior_audits', 'internet_search',
                  'class_codes_fit_risk', 'drug_free', 'exp_date', 'operations_hazards_eval',
                  'large_losses_eval', 'schedule_rating_plan', 'osha_website',
                  'experience_mod_worksheet', ]
        # widgets = {'date_signed_wc_acord130': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
        #            'exp_date': SelectDateWidget(years=list(range(start_year, 2030)), months=MONTHS),
        #            'supplemental_application_year': SelectDateWidget(years=list(range(start_year, 2030)), months=MONTHS),
        #            }

"""
F. Underwriter's Analysis, Comments and Pricing Recommendations
"""

class CommentsForm(ModelForm):
    # Added a new field (referral) to form that is not included in the comments model (also is not saved to comments model)
    referral = forms.CharField(disabled=True, required=False)

    class Meta:
        model = models.Comments
        fields = ['description', 'additional_risk_characteristics', 'class_fit', 'experience_mod_analysis', 'loss_history', 'wage', 'payroll_comments',
                  'recommendations', 'overall_quality', 'total_employees', 'fulltime_employees', 'parttime_employees', 'ee_drivers', 'owner_ops', 'exposed_employees',
                  'referral']

    def set_referral_field(self, carrier, ee_drivers, owner_ops):
        # Set referral field value and label
        if carrier == 'QBE':
            percent_req = 30
        else:
            percent_req = 25

        if ee_drivers is None or owner_ops is None:
            sum_owner_drivers = 0
        else:
            sum_owner_drivers = owner_ops + ee_drivers

        if sum_owner_drivers == 0:
            referral_percentage = 0
        else:
            referral_percentage = owner_ops / (sum_owner_drivers)

        self.fields['referral'] = forms.CharField(
            label=f'Refer if > {percent_req}%', initial=f'{referral_percentage:.0%}', disabled=True, required=False)

"""
G. Claim Details
"""

class ClaimsForm(ModelForm):
    class Meta:
        model = models.Claims
        # fields = ['doi', 'claimant', 'status', 'litigated',
        #           'paid', 'incurred', 'injury_description']
        widgets = {'doi': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
                   'injury_description': Textarea(attrs={'rows': 3, 'cols': 30}),
                   }
        exclude = ('id', 'generalinfo', 'created_date',
                   'last_modified_by', 'last_modified_date',)


ClaimsFormSet = inlineformset_factory(parent_model=models.GeneralInfo, model=models.Claims, form=ClaimsForm, fields=[

                                      'doi', 'claimant', 'status', 'litigated', 'paid', 'incurred', 'injury_description'], min_num=1, max_num=50, extra=0)

ClaimFormSet = forms.modelformset_factory(
    form=ClaimsForm, model=models.Claims, min_num=1, max_num=5, extra=5)

class EvalUnderwriterForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['referral_reason'].widget.attrs.update(
            {'placeholder': 'If yes, enter reason'})
        self.fields['internal_referral_reason'].widget.attrs.update(
            {'placeholder': 'If yes, enter reason'})

    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.EvalUnderwriter
        fields = ['underwriter', 'date', 'underwriting_management', 'management_date', 'referral_required', 'referral_reason',
                  'company_approval_date', 'internal_referral_required', 'internal_referral_reason', 'class_codes_fit_guidelines']
        widgets = {
            # 'date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
            # 'management_date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
            # 'update_date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
            # 'company_approval_date': SelectDateWidget(years=list(range(start_year, 2030)), months=MONTHS)
        }

"""
H. MIA Notes
"""

class NotesForm(ModelForm):
    class Meta:
        months = {
            1: '01', 2: '02', 3: '03', 4: '04',
            5: '05', 6: '06', 7: '07', 8: '08',
            9: '09', 10: '10', 11: '11', 12: '12'
        }
        model = models.Notes
        fields = ['exposure', 'safer_scores', 'osha_violations', 'website_address',
                  'internet_search_results', 'non_trucking_exposure', 'hiring_practices',
                  'loss_control_report_date', 'loss_control_report', ]
        widgets = {
            # 'loss_control_report_date': SelectDateWidget(years=range(start_year, 2030), months=MONTHS),
            'safer_scores': Textarea(attrs={'rows': 3, 'cols': 30})
        }

class RenewalTargetForm(ModelForm):
    class Meta:
        model = models.RenewalTargetRateChange
        fields = ['segment_target_increase',
                  'loss_history_modification', 'exposure_modification']

class ActualRenewalForm(ModelForm):
    class Meta:
        model = models.ActualRenewalRateChange
        fields = ['exp_rate', 'exp_cr_db',
                  'ren_rate', 'ren_cr_db', 'comments']

"""
Form to upload workbooks
"""

class UploadFileForm(ModelForm):
    file = forms.FileField(label='Select a Risk Eval Form')

    class Meta:
        model = models.Upload
        fields = ['form_type', ]

"""
Form to export data to workbooks
"""

class ExportForm(ModelForm):
    #export_to_webdocs = forms.BooleanField(required=False, help_text="Check if you want to export to Webdocs as final submission")
    class Meta:
        model = models.Export
        fields = ['comments', 'export_to_webdocs']

class LoggingHeaderForm(ModelForm):
    class Meta:
        model = models.LoggingHeader
        fields = ['payroll_productions_based', 'waiver_subrogation', 'officers', 'individual_partners', 'mia_paid_reports_on_time',
                  'written_safety_plan', 'lock_out_tag', 'ppe_enforcement', 'drug_alcohol_testing', 'new_employee_training',
                  'vehicle_equipment_maintenance_plan', 'employee_first_aid_cpr', 'bilingual_communication', 'production_rated', 'flammables_proper_storage',
                  'pricing_comments']

class LoggingExposureForm(ModelForm):
    class Meta:
        model = models.LoggingExposureCategories
        fields = ['general_operations', 'terrain', 'losses_past_3yrs', 'business_experience', 'log_hauling_auto',
                  'owned_auto_driver_experience', 'owned_auto_mvr', 'safety', 'loss_handling_and_trends', 'employee_turnover',
                  'subcontracting', 'financial']

"""
Unerwriter Special Notes (Mechanical)
"""

class MechanicalHeaderForm(ModelForm):
    class Meta:
        model = models.MechanicalHeader
        fields = ['waiver_subrogation', 'officers', 'individual_partners', 'mia_paid_reports_on_time',
                  'written_safety_plan', 'optimizing_equipment', 'optimizing_equipment_description', 'dust_collection_system',
                  'dust_collection_system_description', 'housekeeping', 'lock_out_tag', 'ppe_enforcement', 'drug_alcohol_testing',
                  'new_employee_training', 'vehicle_equipment_maintenance_plan', 'first_aid_training', 'bilingual_communication',
                  'flammables_properly_stored', 'pricing_comments']

class MechanicalCategoriesForm(ModelForm):
    class Meta:
        model = models.MechanicalCategories
        fields = ['cutting_operations', 'dust_collection', 'forklift_usage', 'losses_past_3yrs',
                  'business_experience', 'cdl_auto_exposure', 'owned_auto_driver_experience', 'owned_auto_mvr',
                  'safety', 'loss_handling_and_trends', 'employee_turnover', 'subcontracting', 'financial']

"""
Unerwriter Special Notes (Wood Manual)
"""

class WoodManualHeaderForm(ModelForm):
    class Meta:
        model = models.WoodManualHeader
        fields = ['waiver_subrogation', 'officers', 'individual_partners', 'mia_paid_reports_on_time',
                  'written_safety_plan', 'management_routine_inspections', 'dust_free_work_environment',
                  'machines_properly_guarded', 'power_hand_tools_mfg_instructions', 'lock_out_tag', 'ppe_enforcement',
                  'drug_alcohol_testing', 'new_employee_training', 'vehicle_equipment_maintenance_plan', 'first_aid_training',
                  'bilingual_communication', 'flammables_properly_stored', 'pricing_comments']

class WoodMechanicalCategoriesForm(ModelForm):
    class Meta:
        model = models.WoodMechanicalCategories
        fields = ['operations_housekeeping', 'forklift_usage', 'losses_past_3yrs', 'business_experience',
                  'cdl_auto_exposure', 'owned_auto_driver_experience', 'owned_auto_mvr', 'safety', 'loss_handling_and_trends',
                  'employee_turnover', 'subcontracting', 'financial']

"""
MIA Risk Quality Pricing Score
"""

class ScoreForm(ModelForm):
    class Meta:
        model = models.Score
        fields = ['class_fit', 'wages', 'safety_and_controls', 'management']
