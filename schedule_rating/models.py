from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django import forms
from risk_eval.models import GeneralInfo
from multiselectfield import MultiSelectField
from django.core.validators import MaxValueValidator, MinValueValidator


DATA_SET_choices = [(x, x) for x in ('MP', 'CP', 'CE', 'NI', 'PA', 'WF')]


STATE_choices = [
                ('AL','AL'), ('AK','AK'), 
                ('AZ','AZ'), ('AR','AR'), 
                ('CA','CA'), ('CO','CO'), 
                ('CT','CT'), ('DE','DE'), 
                ('D.C.', 'D.C.'),
                #('FL','FL'), 
                ('GA','GA'),
                #('HI','HI'), 
                ('ID','ID'), 
                ('IL','IL'), ('IN','IN'), 
                ('IA','IA'), ('KS','KS'), 
                ('KY','KY'), ('LA','LA'),
                ('ME','ME'), ('MD','MD'),
                #('MA','MA'), 
                ('MI','MI'),
                ('MN','MN'), ('MS','MS'),
                ('MO','MO'), ('MT','MT'),
                ('NE','NE'), ('NV','NV'),
                ('NH','NH'), ('NJ','NJ'),
                ('NM','NM'), ('NY','NY'),
                ('NC','NC'), 
                #('ND','ND'),
                #('OH','OH'), 
                ('OK','OK'),
                #('OR','OR'), 
                ('PA','PA'),
                ('RI','RI'), ('SC','SC'),
                ('SD','SD'), ('TN','TN'),
                ('TX','TX'), ('UT','UT'),
                ('VT','VT'), ('VA','VA'), 
                #('WA','WA'), 
                ('WV','WV'),
                #('WI','WI'), ('WY','WY'),
                ]


UW_choices = [('ARC', 'ARC'),
              ('CMC', 'CMC'),
              ('DRA', 'DRA'),
              ('EER', 'EER'),
              ('JAL', 'JAL'),
              ('JLE', 'JLE'),
              ('KCO', 'KCO'),
              ('KJF', 'KJF'),
              ('KLA', 'KLA'),
              ('MBA', 'MBA'),
              ('MHR', 'MHR'),
              ('MLA', 'MLA'),
              ('NSH', 'NSH'),
              ('PPU', 'PPU'),
              ('RBA', 'RBA'),
              ('TBE', 'TBE'),
              ('AMA', 'AMA'),
              ('', ''),
              ]

FORMTYPE_choices = [
    ('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')]


"""
Worksheet Prep
"""

class SRHeader(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=200, choices = [('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')], 
        default='BH', help_text="""Schedule Rating fields differ between BH and QBE. 
            Please choose wisely. Changing between BH and QBE may delete data.""",
        verbose_name="Form Type")
    named_insured = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Name Insured")
    carrier = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier")
    carrier_code = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier Code")
    dba = models.CharField(max_length=200, null= True, blank=True, verbose_name="DBA")
    uw = models.CharField(max_length=3, choices=UW_choices,
                          null= True, blank=True, verbose_name="UW")
    uw_full_name = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="UW Full Name")
    term = models.CharField(max_length=200, null= True, blank=True)
    unique_number = models.IntegerField(null=True, blank=True, 
        verbose_name="USub (Unique) Number")
    agent_number = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Agent Number")
    effective_date = models.DateField(null=True, blank=True, 
        verbose_name="Effective Date")
    expiration_date = models.DateField(null=True, blank=True, 
        verbose_name="Expiration Date")
    policy_number = models.IntegerField(null=True, blank=True,
        verbose_name="Policy Number")
    data_set = models.CharField(max_length=200, null= True, blank=True, 
        choices = DATA_SET_choices, verbose_name="Data Set",
        help_text="QBE applicable only")
    account_number = models.IntegerField(null=True, blank=True, 
        verbose_name="Account Number")
    date_prepared= models.DateField(null=True, blank=True, verbose_name="Date Prepared")
    quote_number = models.IntegerField(null=True, blank=True, verbose_name="Quote Number")
    # this will just be the pk of the user
    created_by = models.CharField(max_length=10, null=True, blank=True,)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)
    upload_id = models.CharField(max_length=10, null=True, blank=True)


class SRStates(models.Model):
    header= models.ForeignKey(SRHeader, on_delete=models.CASCADE)
    states= MultiSelectField(choices=STATE_choices) # stores a list of states


"""
Individual States Page
"""
class StateHeader(models.Model):
    header = models.ForeignKey(SRHeader, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=200, choices = [('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')], 
        default='BH', help_text="""Schedule Rating fields differ between BH and QBE""")
    state = models.CharField(max_length=10, null=False, blank=True, choices=STATE_choices,
        help_text="Do NOT edit")
    risk_location = models.CharField(max_length=200, null= True, blank=True,
        help_text="Risk location or address")
    effective_date = models.DateField(null=True, blank=True, 
        help_text = "Effective Date of Schedule Rating (if applicable)", 
        verbose_name="Effective Date") # adding this for MT, NE
    carrier = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier")
    carrier_code = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier Code")
    last_modified_by = models.IntegerField(null=True, blank=True)


class StateLines(models.Model):
    header = models.ForeignKey(StateHeader, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, null=False, blank=True, choices=STATE_choices)
    category = models.CharField(max_length=100, null=False, blank=False)
    range_available = models.CharField(max_length=100)
    credit_applied =  models.IntegerField(null=True, blank=True)
    debit_applied = models.IntegerField(null=True, blank=True)
    reason_basis = models.TextField(null=True, blank=True)


class CAHeader(models.Model):
    header = models.ForeignKey(SRHeader, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=200, choices = [('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')], 
        default='BH', help_text="""Schedule Rating fields differ between BH and QBE""")
    state = models.CharField(max_length=2, null=False, blank=True, 
        choices=[("CA", "CA")], default="CA")
    risk_location = models.CharField(max_length=200, null= True, blank=True)
    effective_date = models.DateField(null=True, blank=True, 
        help_text = "Effective Date of Schedule Rating", verbose_name="Effective Date")
    carrier = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier")
    carrier_code = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier Code")
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)


class CALines(models.Model):
    header = models.ForeignKey(CAHeader, on_delete=models.CASCADE)
    state = models.CharField(max_length=2, null=False, blank=True, 
        choices=[("CA", "CA")], default="CA")
    category = models.CharField(max_length=100)
    range_available = models.CharField(max_length=100)
    below_average = models.IntegerField(null=True, blank=True)
    average = models.IntegerField(null=True, blank=True)
    superior = models.IntegerField(null=True, blank=True)
    reason_basis = models.TextField(null=True, blank=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)


class AdaptedStateHeader(models.Model):
    """
    Applicable for BH:
        NM, SD, VT
    Difference from V2 is that this includes loss prevention survey
    """
    header = models.ForeignKey(SRHeader, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=200, choices = [('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')], 
        default='BH', help_text="""Schedule Rating fields differ between BH and QBE""")
    state = models.CharField(max_length=10, null=False, blank=True, 
        choices=STATE_choices, help_text="Do NOT edit")
    status = models.CharField(max_length=10, null=True, blank=True, 
        choices = [('New', 'New'), ('Renewal', 'Renewal')],
        help_text="New or Renewal?")
    risk_location = models.CharField(max_length=200, null= True, blank=True, 
        help_text = "Risk Address", verbose_name="Risk Location")
    risk_id = models.CharField(max_length=200, null= True, blank=True,
        help_text = "Risk Identification Number if applicable", verbose_name="Risk ID")
    # is this date for the schedule rating? or account?
    effective_date = models.DateField(null=True, blank=True, 
        help_text = "Effective Date of Schedule Rating (if applicable)", 
        verbose_name="Effective Date")
    # SD loss survey format
    loss_survey_format = models.CharField(max_length=50, null=True, blank=True,
        choices = [('-', '-'), ('Physical on-site inspection', 'Physical on-site inspection'), 
            ('Telephone survey', 'Telephone survey'), ('Electronic Survey', 'Electronic Survey'), 
            ('n/a', 'n/a')],
        help_text="Specific type of survey physical on-site inspection, telephone survey, or electronic survey")
    # loss prevention survey is applircable for 
    # NH, VT
    loss_prevention_survey = models.CharField(max_length=10, null=True, blank=True,
        choices = [('Yes', 'Yes'), ('No', 'No')],
        help_text="Loss Prevention Survey Completed?")
    loss_prevention_survey_date = models.DateField(null=True, blank=True,
        help_text = "Date loss prevention survey was completed", verbose_name="Date")
    # standard premium is applicable to KS, SD, NM, VT
    ncci_rates = models.CharField(max_length=20, verbose_name="NCCI Rates",
        choices = [("Yes", "Yes"), ("No", "No")], null=True, blank=True, 
        help_text="Are NCCI Rates being used without deviation? ") # AZ specific
    standard_premium_exists = models.CharField(max_length=10, null=True, blank=True,
        choices = [('Yes', 'Yes'), ('No', 'No')],
        help_text="Is there a minimum premium?") # SD, VT
    standard_premium = models.DecimalField(null=True, blank=True, 
        decimal_places=2, max_digits=10,
        help_text="State Estimated Standard Premium")
    az_sr_plan_2 = models.CharField(max_length=20, verbose_name="AZ Plan II",
        choices = [("Yes", "Yes"), ("No", "No")], null=True, blank=True, 
        help_text="Is Arizona Schedule Rating Plan II being used?") # AZ specific
    # rating_eligibility is AZ, NM specific
    rating_eligibility = models.CharField(max_length=10, null=True, blank=True,
        choices = [('Yes', 'Yes'), ('No', 'No')],
        help_text="Does Estimated Standard Premium Equal or Exceed Current Experience Rating Eligibility")
    wcpr_credits = models.IntegerField(null=True, blank=True, 
        verbose_name="WCPR Credits",
        help_text="""Do Oklahoma Workers Compensation Premium Reduction (WCPR) credits apply to this policy? 
            If so, write the WCPR credits in this space""",
            validators=[MinValueValidator(0), MaxValueValidator(15)])
    merit_plan_credits = models.IntegerField(null=True, blank=True, 
        validators=[MinValueValidator(-5), MaxValueValidator(5)],
        help_text="""Do Oklahoma Workers Compensation Merit Plan credits or debits apply to this policy? 
            If so, write the write the Merit Plan credits or debits in this space as appropriate.""")
    merit_plan_debits = models.IntegerField(null=True, blank=True,
        validators=[MinValueValidator(-5), MaxValueValidator(5)],
        help_text="""Do Oklahoma Workers Compensation Merit Plan credits or debits apply to this policy? 
            If so, write the write the Merit Plan credits or debits in this space as appropriate.""")
    carrier = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier")
    carrier_code = models.CharField(max_length=200, null= True, blank=True,
        verbose_name="Carrier Code")
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class AdaptedStateLines(models.Model):
    header = models.ForeignKey(AdaptedStateHeader, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, null=False, blank=True, 
        choices=STATE_choices, default="NM")
    category = models.CharField(max_length=100, null=False, blank=False)
    range_available = models.CharField(max_length=100)
    # previous credit/debit applies to:
    # GA, IL, LA, ME, NJ, NM
    previous_credit_applied =  models.IntegerField(null=True, blank=True, 
        help_text="If renewal, previous years")
    previous_debit_applied = models.IntegerField(null=True, blank=True,
        help_text="If renewal, previous years")
    credit_applied =  models.IntegerField(null=True, blank=True)
    debit_applied = models.IntegerField(null=True, blank=True)
    reason_basis = models.TextField(null=True, blank=True)


"""
Uploads table for SR Excel workbooks for storage
"""


class Upload(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=10, null=True, blank=True)



"""
Exports to SR Excel workbooks 
"""

class Export(models.Model):
    header = models.ForeignKey(SRHeader, on_delete = models.CASCADE, null=True, blank=True)
    form_type = models.CharField(choices=FORMTYPE_choices, max_length=50,
        help_text="Do not change form type")
    comments = models.TextField(null=True, blank=True, 
        help_text = "Additional comments regarding this Schedule Rating export")
    file_name = models.CharField(max_length = 200, blank=True, null=True,
        help_text="If file name is blank, then the file must have not exported successfully")
    export_to_webdocs = models.BooleanField(default=False, 
        verbose_name= "Export to Webdocs",
        help_text="Check if you want to export to Webdocs as final submission")
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=10, null=True, blank=True)

