from tkinter import DISABLED
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
YEAR_choices = [(str(x), str(x)) for x in range(1990, 2030)]

DATA_SET_choices = [(x, x) for x in ('MP', 'CP', 'CE', 'NI', 'PA', 'WF')]

UW_choices = [('', ''),
              ('AMA', 'AMA'),
              ('ARC', 'ARC'),
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
              ('SSL', 'SSL'),
              ('TBE', 'TBE'),
              ]

TERM_choices = [('', ''), ('New', 'New'), ('Renewal', 'Renewal'),
                ('Rewrite', 'Rewrite')]

STATE_choices = [('', ''), ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'),
                 ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE',
                                                             'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'),
                 ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL',
                                                     'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
                 ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA',
                                                        'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
                 ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN',
                                                               'Minnesota'), ('MS', 'Mississippi'),
                 ('MO', 'Missouri'), ('MT', 'Montana'), ('NE',
                                                         'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'),
                 ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY',
                                                              'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'),
                 ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR',
                                                      'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
                 ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN',
                                                                    'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
                 ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA',
                                                         'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'),
                 ('WY', 'Wyoming')]

TERM_FREQUENCY_choices = [('Per Expiring', 'Per Expiring'), ('Per Prior Audit', 'Per Prior Audit'),
                          ('Monthly Report', 'Monthly Report'), ('Per Agent', 'Per Agent'), ('', '')]

YES_NO_choices = [('Yes', 'Yes'), ('No', 'No'), ('', ''),
                  ('Not Applicable', 'Not Applicable'), ('N/A', 'N/A')]

YES_NO_ONLY_choices = [('', ''), ('Yes', 'Yes'), ('No', 'No')]

FIN_INDICATORS_choices = [('Insufficient Data', 'Insufficient Data'), ('Not Applicable', 'Not Applicable'), ('High Risk', 'High Risk'), ('Med.-High Risk', 'Med.-High Risk'),
                          ('Med. Risk', 'Med. Risk'), ('Med.-Low Risk', 'Med.-Low Risk'), ('Low Risk', 'Low Risk'), ('Recent Bankruptcy', 'Recent Bankruptcy')]

ATTITUDE_choices = [('Average Concern', 'Average Concern'), ('Higher Than Average Concern',
                                                             'Higher Than Average Concern'), ('Very High Concern', 'Very High Concern'), ('', '')]


EXPOSURES_choices = [('Much less hazardous or significantly better controlled than the average risk contemplated by class/industry', 'Much less hazardous or significantly better controlled than the average risk contemplated by class/industry'),
                     ('Less hazardous or somewhat better controlled than the average risk contemplated by class/industry',
                      'Less hazardous or somewhat better controlled than the average risk contemplated by class/industry'),
                     ('Average for class/industry', 'Average for class/industry'),
                     ('More hazardous than the average risk contemplated by class/industry',
                      'More hazardous than the average risk contemplated by class/industry'),
                     ('', '')]

FORMTYPE_choices = [
    ('', ''), ('BH', 'Berkshire Hathaway'), ('QBE', 'QBE')]

QUALITY_POINT_GRADE_choices = [
    ('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4'), ('Q5', 'Q5'), ('Q6', 'Q6'), ('', '')]

"""
Section A
"""

class GeneralInfo(models.Model):
    named_insured = models.CharField(
        max_length=200, verbose_name="Name Insured")
    carrier = models.CharField(default='', max_length=10,
                               null=False, blank=False, verbose_name="Carrier",
                               help_text="Choose a carrier for the Risk Eval. This affects output calculations",
                               choices=FORMTYPE_choices)
    dba = models.CharField(max_length=200, null=True,
                           blank=True, verbose_name="DBA")
    business_overview = models.TextField(null=True, blank=True)
    uw = models.CharField(max_length=20, choices=UW_choices,
                          null=False, blank=False,
                          verbose_name="UW")
    effective_date = models.DateField(null=True, blank=True,
                                      verbose_name="Effective Date")
    expiration_date = models.DateField(null=True, blank=True,
                                       verbose_name="Expiration Date")
    term = models.CharField(
        max_length=200, choices=TERM_choices, null=True, blank=False,
        help_text="Is this Risk Eval for a new business or renewal or rewrite?")
    state = models.CharField(
        max_length=2, choices=STATE_choices, null=True, blank=False)
    agent_number = models.CharField(max_length=200, null=True, blank=False)
    agency_name = models.CharField(max_length=200, null=True, blank=False)
    quote_number = models.IntegerField(null=True, blank=False)
    unique_number = models.CharField(max_length=10, null=False, blank=False,
                                        help_text="This field must be populated")
    account_number = models.IntegerField(null=True, blank=True)
    data_set = models.CharField(max_length=2, null=True, blank=True,
                                choices=DATA_SET_choices, verbose_name="Data Set",
                                help_text="QBE applicable only")
    number_employees = models.IntegerField(null=True, blank=True)
    projected_payroll = models.PositiveIntegerField(default=1,
                                                    null=False, blank=False,
                                                    verbose_name="Projected Payroll for Upcoming Term",
                                                    help_text="Necessary for Account and Loss calculations")
    term_frequency = models.CharField(
        max_length=200, choices=TERM_FREQUENCY_choices, null=True, blank=True,
        verbose_name="Projected Payroll from")
    projected_base_premium = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Projected Base Premium for Upcoming Term",
        help_text="This field is calculated from the Class Codes & Payroll section below")
    projected_net_premium = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Projected Net Premium for Upcoming Term")
    governing_class_code = models.CharField(max_length=10, null=True, blank=True,
                                            verbose_name="Governing Class Code")
    # this will just be the pk of the user
    created_by = models.CharField(max_length=10, null=True, blank=True,)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)
    upload_id = models.IntegerField(null=True, blank=True)

class GeneralInfoPremium(models.Model):
    generalinfo = models.ForeignKey(
        GeneralInfo, on_delete=models.CASCADE, related_name="generalinfo")
    state = models.CharField(
        max_length=2, choices=STATE_choices, null=True, blank=True)
    class_code = models.IntegerField(null=True, blank=True)
    manual_premium = models.PositiveIntegerField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = "<ManualPremium: (State: {} Class Code: {})>".format(
            self.state, self.class_code)
        return label

# the other models were moved to models_notes.txt
# they will be added incrementally

"""
Section B Account History and Loss Rating
"""

class AccountHistory(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    policy_period = models.IntegerField(blank=True, null=True)  # has data
    effective_date = models.DateField(blank=False, null=False)
    expiration_date = models.DateField(blank=False, null=False)
    written_premium = models.PositiveIntegerField(
        null=True,
        help_text="Has to be populated for calculations")
    incurred_losses = models.PositiveIntegerField(
        blank=True, null=True)
    paid_losses = models.PositiveIntegerField(
        blank=True, null=True)
    total_claims = models.IntegerField(
        blank=True, null=True)
    total_indemnity_claims = models.IntegerField(
        blank=True, null=True)
    indemnity_claims = models.IntegerField(
        blank=True, null=True,
        help_text="Indemnity Claims <= $2,000")  # number of claims <= 2000
    open_claims = models.IntegerField(
        blank=True, null=True)
    #actual_loss_ratio = models.DecimalField(
     #   decimal_places=1, max_digits=10, blank=True, null=True)
    no_history = models.BooleanField(default=False,
                                     verbose_name="No History", help_text="Exclude policy period from calculations because there is no history")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = "<AccountHistory: {}>".format(self.effective_date)
        return label

class LossRatingValuation(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    policy_period = models.IntegerField(blank=False, null=False)
    valuation_date = models.DateField(blank=True, null=True)
    """age = models.IntegerField(blank=True, null=True)  # months
    ## BH ##
      industry_ldf = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    trended_payroll = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    ultimate_reported_claims = models.DecimalField(
        decimal_places=3, max_digits=10, blank=True, null=True)
    ultimate_indemnity_claims = models.IntegerField(blank=True, null=True) """
    # user entry
    payroll = models.PositiveIntegerField(
        blank=True, null=True)
    prior_carrier = models.CharField(max_length=250, blank=True, null=True)
    """bh_developed_loss_ratio = models.DecimalField(
        decimal_places=6, max_digits=10, blank=True, null=True)
    ult_clm_ratio = models.DecimalField(
        decimal_places=6, max_digits=10, blank=True, null=True)
    ## QBE ##
    developed_losses = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)  # QBE ONLY
    bf_losses = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)  # QBE ONLY
    selected_ult_losses = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)  # QBE ONLY
    loss_trend_factor = models.DecimalField(
        decimal_places=6, max_digits=10, blank=True, null=True)  # QBE ONLY
    ult_trended_losses = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)  # QBE ONLY
    qbe_developed_loss_ratio = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)  # QBE ONLY """
    no_history = models.BooleanField(default=False,
                                     verbose_name="No History", help_text="Exclude policy period from calculations because there is no history")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = "<LossRating: {}>".format(self.valuation_date)
        return label

"""
C. Risk Characteristics
"""

class RiskHeader(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    group_med = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Group medical insurance provided by employer")
    active_injury_program = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Active injury & illness prevention program")
    return_to_work_program = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Return to work or modified work program in place")
    loss_free_safety_incentive = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Loss free safety incentive program in place")
    safety_meetings = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Safety Meetings held routinely")
    financial_indicators = models.CharField(
        choices=FIN_INDICATORS_choices, max_length=500,
        blank=True, null=True,
        verbose_name="Financial indicators or credit scores")
    score = models.IntegerField(null=True, blank=True)
    management_attitude = models.CharField(
        choices=ATTITUDE_choices, max_length=500, blank=True, null=True,
        verbose_name="Management attitude toward workplace safety & loss control is:")
    exposures = models.CharField(
        choices=EXPOSURES_choices, max_length=500, blank=True, null=True,
        verbose_name="Operations/exposures are determined to be:")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class RiskExmod(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True)
    exmod_val = models.DecimalField(
        decimal_places=3, max_digits=10, blank=True, null=True,
        verbose_name="Exmod Value")
    """loss_rate = models.DecimalField(blank=True, null=True,
                                    verbose_name="Loss Rate", decimal_places=4, max_digits=6,
                                    help_text="Field is automatically calculated")"""
    no_history = models.BooleanField(default=False,
                                     verbose_name="No History", help_text="Exclude year from calculations because there is no history")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Section D Checklist (Items documented and evaluated)
"""

class Checklist(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    date_signed_wc_acord130 = models.DateField(null=True, blank=True,
                                               verbose_name="Date of signed WC Acord 130 application")
    supplemental_application = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Supplemental application")
    supplemental_application_year = models.DateField(
        blank=True, null=True,
        verbose_name="Date of signed Supplemental Application")
    loss_control_report = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Loss control report/pre-inspection")
    prior_audits = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Prior audits/financials/credit report")
    internet_search = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Internet Search")
    class_codes_fit_risk = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="All class codes for risk fit guidelines")
    drug_free = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Drug Free Workplace Certificate")
    operations_hazards_eval = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Operations/hazards evaluated")
    large_losses_eval = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Large losses evaluated")
    schedule_rating_plan = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Schedule rating plan")
    osha_website = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="OSHA Website")
    experience_mod_worksheet = models.CharField(
        max_length=20, choices=YES_NO_choices, blank=True, null=True,
        verbose_name="Experience Mod Worksheet")
    exp_date = models.DateField(null=True, blank=True,
                                verbose_name="Exp. Date",
                                help_text="Drug Free Workcplace Certificate Expiration Date")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Section F
"""

class Comments(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True,
                                   verbose_name="Description of Operations")
    additional_risk_characteristics = models.TextField(blank=True, null=True,
                                                       verbose_name="Additional Risk Characteristics")
    class_fit = models.TextField(blank=True, null=True)
    experience_mod_analysis = models.TextField(blank=True, null=True,
                                               verbose_name="Experience Mod Analysis")
    loss_history = models.TextField(blank=True, null=True,
                                    verbose_name="Loss History - Sev./Freq. Analysis")
    wage = models.TextField(blank=True, null=True)
    payroll_comments = models.TextField(blank=True, null=True,
                                        verbose_name="Payroll Comments")
    recommendations = models.TextField(blank=True, null=True,
                                       verbose_name="Recommendation/Summary")
    overall_quality = models.CharField(
        max_length=5, blank=True, null=True, choices=QUALITY_POINT_GRADE_choices,
        verbose_name="Overall Quality Point Grade")
    total_employees = models.IntegerField(null=True, blank=True,
                                          verbose_name="Total Number of Employees")
    fulltime_employees = models.IntegerField(null=True, blank=True,
                                             verbose_name="Full-time Employees")
    parttime_employees = models.IntegerField(null=True, blank=True,
                                             verbose_name="Part-time Employees")
    ee_drivers = models.IntegerField(null=True, blank=True,
                                     verbose_name="EE Drivers")
    owner_ops = models.IntegerField(null=True, blank=True,
                                    verbose_name="Owner Ops")
    exposed_employees = models.IntegerField(null=True, blank=True,
                                            verbose_name="Number of Employees Exposed",
                                            help_text="Complete this field only when the total number of employees exceeds 100")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Section G Claim Details
"""

class Claims(models.Model):
    STATUS_CHOICES = (
        ("Open", "Open"),
        ("Closed", "Closed"),
        ("Unknown", "Unknown"),
    )
    LITIGATED_CHOICES = (
        ("Yes", "Yes"),
        ("No", "No"),
        ("Unknown", "Unknown"),
    )
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    doi = models.DateField(blank=True, null=True,
                           verbose_name="DOI",
                           help_text="DOI is a required field.")
    claimant = models.CharField(null=True, blank=True, max_length=100)
    injury_description = models.CharField(
        blank=True, null=True, max_length=700)
    status = models.CharField(choices=STATUS_CHOICES,
                              null=True, blank=True, max_length=100)
    litigated = models.CharField(
        choices=LITIGATED_CHOICES, null=True, blank=True, max_length=100)
    paid = models.PositiveIntegerField(null=True, blank=True)
    incurred = models.PositiveIntegerField(
        null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = "<Claim: {}>".format(self.doi)
        return label

class EvalUnderwriter(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True,
                            default=timezone.now,
                            verbose_name="Underwritten Date",
                            help_text="Underwritten Date")
    underwriter = models.CharField(null=True, blank=True, max_length=100,
                                   verbose_name="Underwriter's Name")
    underwriting_management = models.CharField(
        blank=True, null=True, max_length=100)
    management_date = models.DateField(null=True, blank=True,
                                       verbose_name="Approval Date",
                                       help_text="Date Risk Eval was Approved")
    referral_required = models.CharField(
        max_length=20, choices=YES_NO_ONLY_choices, blank=True, null=True,
        verbose_name="Referral to company required?")
    referral_reason = models.TextField(null=True, blank=True,
                                       verbose_name="Referral Reason")
    company_approval_date = models.DateField(null=True, blank=True,
                                             verbose_name="Date of Approval",
                                             help_text="If referral not required due to prior company approval, indicate date of approval")
    internal_referral_required = models.CharField(
        max_length=20, choices=YES_NO_ONLY_choices, blank=True, null=True,
        verbose_name="Is internal referral required?")
    internal_referral_reason = models.CharField(
        null=True, blank=True, max_length=500,
        verbose_name="Referral Reason")
    class_codes_fit_guidelines = models.CharField(
        max_length=20, choices=YES_NO_ONLY_choices, blank=True, null=True,
        verbose_name="Class codes fit guidelines",
        help_text="""Do all class codes on the quote fit within the company guidelines? 
            If no, this requires internal referral before seeking company approval""")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Section H MIA Notes
"""

class Notes(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    exposure = models.TextField(null=True, blank=True,
                                verbose_name="Subcontractor / Owner operator Exposure")
    safer_scores = models.TextField(null=True, blank=True,
                                    verbose_name="Safer Scores, if applicable")
    osha_violations = models.TextField(null=True, blank=True,
                                       verbose_name="OSHA Violations - Contractors & Mfg Risks")
    website_address = models.CharField(null=True, blank=True, max_length=500)
    internet_search_results = models.TextField(
        null=True, blank=True)
    non_trucking_exposure = models.TextField(
        null=True, blank=True,
        verbose_name="Non-trucking Delivery Exposure, if applicable")
    hiring_practices = models.TextField(null=True, blank=True)
    loss_control_report_date = models.DateField(null=True, blank=True,
                                                verbose_name="Date of Loss Control Report")
    loss_control_report = models.TextField(null=True, blank=True,
                                           verbose_name="Loss Control Findings")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class RenewalTargetRateChange(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    # renewal target rate increase
    """renewal_rate_increase = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True,
                                                verbose_name="Renewal Target Rate Change",
                                                help_text="This field is calculated")"""
    segment_target_increase = models.DecimalField(default=0,
                                                  decimal_places=2, max_digits=10, null=False, verbose_name="Segment Target Increase")
    loss_history_modification = models.DecimalField(default=0,
                                                    decimal_places=2, max_digits=10, null=False, verbose_name="Loss History Modification")
    exposure_modification = models.DecimalField(default=0,
                                                decimal_places=2, max_digits=10, null=False, verbose_name="Exposure Modification")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class ActualRenewalRateChange(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    # actual renewal rate increase
    """ actual_renewal_rate_change = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True,
        verbose_name="Actual Renewal Rate Change",
        help_text="This field is calculated")  # calculated """
    exp_rate = models.DecimalField(default=0,
                                   decimal_places=2, max_digits=10, null=False,
                                   verbose_name="Exp Rate")  # user entry
    exp_cr_db = models.DecimalField(default=0,
                                    decimal_places=2, max_digits=10, null=False,
                                    verbose_name="Exp Cr or Db")  # user entry
    """exp_adj_rate = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True,
        verbose_name="Exp Adj Rate",
        help_text="This field is calculated")  # calculated"""
    ren_rate = models.DecimalField(default=0,
                                   decimal_places=2, max_digits=10, null=False,
                                   verbose_name="Ren Rate")  # user entry
    ren_cr_db = models.DecimalField(default=0,
                                    decimal_places=2, max_digits=10, null=False,
                                    verbose_name="Ren Cr or Db")  # user entry
    """ren_adj_rate = models.DecimalField(
        decimal_places=2, max_digits=10, null=True, blank=True,
        verbose_name="Ren Adj Rate",
        help_text="This field is calculated")  # calculated"""
    comments = models.CharField(
        null=True, blank=True, max_length=500,
        verbose_name="Rate Change Comments")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Uploads table for BH and QBE Excel workbooks for storage
"""

class Upload(models.Model):
    form_type = models.CharField(choices=FORMTYPE_choices, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=10, null=True, blank=True)

"""
Exports to BH and QBE Excel workbooks
"""

class Export(models.Model):
    generalinfo = models.ForeignKey(
        GeneralInfo, on_delete=models.CASCADE, null=True, blank=True)
    form_type = models.CharField(choices=FORMTYPE_choices, max_length=50,
                                 blank=True, null=True)
    comments = models.TextField(null=True, blank=True,
                                help_text="Additional comments regarding this risk eval export")
    export_to_webdocs = models.BooleanField(default=False,
                                            verbose_name="Export to Webdocs",
                                            help_text="Check if you want to export to Webdocs as final submission")
    file_name = models.CharField(max_length=200, blank=True, null=True,
                                 help_text="If file name is blank, then the file must have not exported successfully")
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=10, null=True, blank=True)

"""
Underwriter Special Notes (Logging)
"""

class LoggingHeader(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    payroll_productions_based = models.CharField(max_length=15, blank=True, null=True,
                                                 choices=[
                                                     ('Payroll', 'Payroll'), ('Production', 'Production')],
                                                 verbose_name="Payroll or Productions Based")
    waiver_subrogation = models.CharField(max_length=20, blank=True, null=True,
                                          choices=[
                                              ('N/A', 'N/A'), ('Blanket', 'Blanket'), ('Specific', 'Specific')],
                                          verbose_name="Waiver of Subrogation")
    officers = models.CharField(max_length=20, blank=True, null=True,
                                choices=[('N/A', 'N/A'), ('Included',
                                                          'Included'), ('Excluded', 'Excluded')],
                                verbose_name="Officers - included/excluded")
    individual_partners = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[
                                               ('N/A', 'N/A'), ('Included', 'Included'), ('Excluded', 'Excluded')],
                                           verbose_name="Individual/Partners - included/excluded")
    mia_paid_reports_on_time = models.CharField(max_length=20, blank=True, null=True,
                                                choices=[
                                                    ('No', 'No'), ('Yes', 'Yes')],
                                                verbose_name="MIA Paid Monthly Reports on time")

    """Safety programs, mfg equipment and operational procedures"""
    written_safety_plan = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[('No', 'No'),
                                                    ('Yes', 'Yes')],
                                           verbose_name="Written Safety Plan")
    lock_out_tag = models.CharField(max_length=20, blank=True, null=True,
                                    choices=[('No', 'No'), ('Yes', 'Yes')],
                                    verbose_name="Lock Out Tag out program for equipment maintenance")
    ppe_enforcement = models.CharField(max_length=20, blank=True, null=True,
                                       choices=[('No', 'No'), ('Yes', 'Yes')],
                                       verbose_name="Provides and enforces use of PPE")
    drug_alcohol_testing = models.CharField(max_length=20, blank=True, null=True,
                                            choices=[('No', 'No'),
                                                     ('Yes', 'Yes')],
                                            verbose_name="Drug and Alcohol testing program in place")
    new_employee_training = models.CharField(max_length=20, blank=True, null=True,
                                             choices=[('No', 'No'),
                                                      ('Yes', 'Yes')],
                                             verbose_name="New employee training program")
    vehicle_equipment_maintenance_plan = models.CharField(max_length=20, blank=True, null=True,
                                                          choices=[
                                                              ('No', 'No'), ('Yes', 'Yes')],
                                                          verbose_name="Written vehicle and equipment maintenance plan")
    employee_first_aid_cpr = models.CharField(max_length=20, blank=True, null=True,
                                              choices=[('No', 'No'),
                                                       ('Yes', 'Yes')],
                                              verbose_name="Employees trained in first aid and CPR")
    bilingual_communication = models.CharField(max_length=20, blank=True, null=True,
                                               choices=[('No', 'No'),
                                                        ('Yes', 'Yes')],
                                               verbose_name="Bi-lingual communication capability, if needed")
    production_rated = models.CharField(max_length=20, blank=True, null=True,
                                        choices=[('No', 'No'), ('Yes', 'Yes')],
                                        verbose_name="Production rated <25,000")
    flammables_proper_storage = models.CharField(max_length=20, blank=True, null=True,
                                                 choices=[
                                                     ('No', 'No'), ('Yes', 'Yes')],
                                                 verbose_name="Enforces proper storage and use of flammables")
    pricing_comments = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class LoggingExposureCategories(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    general_operations = models.CharField(max_length=50, blank=True, null=True,
                                          choices=[('FAA > 95% mechanized, machine delimbing', 'FAA > 95% mechanized, machine delimbing'),
                                                   ('AA > 90% mechanized, pull thru delimbing',
                                                    'AA > 90% mechanized, pull thru delimbing'),
                                                   ('A > 80% mechanized, manual trimming',
                                                    'A > 80% mechanized, manual trimming'),
                                                   ('BA < 80% mechanized, maunal trimming', 'BA < 80% mechanized, maunal trimming'), ],
                                          verbose_name="General operations")
    terrain = models.CharField(max_length=50, blank=True, null=True,
                               choices=[('FAA Flat or 1st or 2nd thinning operation', 'FAA Flat or 1st or 2nd thinning operation'),
                                        ('AA Flat or clear cut operations',
                                         'AA Flat or clear cut operations'),
                                        ('A Flat to rolling > 75% soft wood cutting',
                                         'A Flat to rolling > 75% soft wood cutting'),
                                        ('BA Hilly with hardwood cutting', 'BA Hilly with hardwood cutting'), ],
                               verbose_name="Terrain")
    losses_past_3yrs = models.CharField(max_length=100, blank=True, null=True,
                                        choices=[('FAA No Losses', 'FAA No Losses'),
                                                 ('AA Loss ratio < 30% w/o auto related WC claims',
                                                  'AA Loss ratio < 30% w/o auto related WC claims'),
                                                 ('A Loss ratio < 50% or related WC claims',
                                                  'A Loss ratio < 50% or related WC claims'),
                                                 ('BA Loss ratio > 50% or claims from uninsured subs', 'BA Loss ratio > 50% or claims from uninsured subs')],
                                        verbose_name="Losses past 3 years")
    business_experience = models.CharField(max_length=100, blank=True, null=True,
                                           choices=[('FAA >10 years continuous in industry', 'FAA >10 years continuous in industry'),
                                                    ('AA 6 to 10 years continuous in industry',
                                                     'AA 6 to 10 years continuous in industry'),
                                                    ('A 3 to 5 years continuous in industry',
                                                     'A 3 to 5 years continuous in industry'),
                                                    ('BA <3 years continuous in industry', 'BA <3 years continuous in industry'), ],
                                           verbose_name="Business Experience")
    log_hauling_auto = models.CharField(max_length=100, blank=True, null=True,
                                        choices=[('FAA No exposure or 100% insured subcontractors', 'FAA No exposure or 100% insured subcontractors'),
                                                 ('AA Owned autos insured and subcontractors',
                                                  'AA Owned autos insured and subcontractors'),
                                                 ('A 100% owned autos',
                                                  'A 100% owned autos'),
                                                 ('BA Any use of uninsured subcontractors', 'BA Any use of uninsured subcontractors'), ],
                                        verbose_name="Log hauling auto")
    owned_auto_driver_experience = models.CharField(max_length=100, blank=True, null=True,
                                                    choices=[('FAA 75% CDL 5 years experience', 'FAA 75% CDL 5 years experience'),
                                                             ('AA 60% of CDL 5 years experience',
                                                              'AA 60% of CDL 5 years experience'),
                                                             ('A 40% of CDL 5 years experience',
                                                              'A 40% of CDL 5 years experience'),
                                                             ('BA <40% of CDL 5 years experience', 'BA <40% of CDL 5 years experience'), ],
                                                    verbose_name="Owned Auto - drivers experience")
    owned_auto_mvr = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA 60% CDL clear <10% borderline', 'FAA 60% CDL clear <10% borderline'),
                                               ('AA 50% to 59% CDL clear <10% borderline',
                                                'AA 50% to 59% CDL clear <10% borderline'),
                                               ('A 40% to 49% CDL clear <10% borderline',
                                                'A 40% to 49% CDL clear <10% borderline'),
                                               ('BA <40% CDL clear and / or >10% borderline', 'BA <40% CDL clear and / or >10% borderline'), ],
                                      verbose_name="Owned Auto - MVR's")
    safety = models.CharField(max_length=100, blank=True, null=True,
                              choices=[('FAA very proactive, anticipates hazards and formal plan in place', 'FAA very proactive, anticipates hazards and formal plan in place'),
                                       ('AA Established policies in plance and active management',
                                        'AA Established policies in plance and active management'),
                                       ('A Aware of major exposures and information plan in place',
                                        'A Aware of major exposures and information plan in place'),
                                       ('BA Management not actively involved and no plan', 'BA Management not actively involved and no plan'), ])
    loss_handling_and_trends = models.CharField(max_length=100, blank=True, null=True,
                                                choices=[('FAA Management has influence and loss results reflect', 'FAA Management has influence and loss results reflect'),
                                                         ('AA Management taking action, review of losses',
                                                          'AA Management taking action, review of losses'),
                                                         ('A Management addresses on a reactive basis',
                                                          'A Management addresses on a reactive basis'),
                                                         ('BA Management casually aware, ineffective approach', 'BA Management casually aware, ineffective approach'), ],
                                                verbose_name="Loss Handling & Trends")
    employee_turnover = models.CharField(max_length=100, blank=True, null=True,
                                         choices=[('FAA low turnover, stable, experienced <10%', 'FAA low turnover, stable, experienced <10%'),
                                                  ('AA low turnover, stable, experience <15%',
                                                   'AA low turnover, stable, experience <15%'),
                                                  ('A average turnover up to 20%',
                                                   'A average turnover up to 20%'),
                                                  ('BA below average turnover >20% turnover rate', 'BA below average turnover >20% turnover rate'), ],
                                         verbose_name="Employee Turnover")
    subcontracting = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA no exposure', 'FAA no exposure'),
                                               ('AA written program with exposure',
                                                'AA written program with exposure'),
                                               ('A no program, requires certificate of insurance',
                                                'A no program, requires certificate of insurance'),
                                               ('BA no program with uninsured subcontractors', 'BA no program with uninsured subcontractors'), ],
                                      verbose_name="Sub-Contracting")
    financial = models.CharField(max_length=100, blank=True, null=True, choices=[('Not included at this time', 'Not included at this time'), ],
                                 default='Not included at this time')
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Underwriter Special Notes (Mechanical)
"""

class MechanicalHeader(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    waiver_subrogation = models.CharField(max_length=20, blank=True, null=True,
                                          choices=[
                                              ('N/A', 'N/A'), ('Blanket', 'Blanket'), ('Specific', 'Specific')],
                                          verbose_name="Waiver of Subrogation")
    officers = models.CharField(max_length=20, blank=True, null=True,
                                choices=[('N/A', 'N/A'), ('Included', 'Included'), ('Excluded', 'Excluded')])
    individual_partners = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[('N/A', 'N/A'), ('Included', 'Included'), ('Excluded', 'Excluded')])
    mia_paid_reports_on_time = models.CharField(max_length=20, blank=True, null=True,
                                                choices=[
                                                    ('No', 'No'), ('Yes', 'Yes')],
                                                verbose_name="MIA Paid Monthly Reports on time")

    """Safety Programs, MFG Equipment and Operational Procedures"""
    written_safety_plan = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[('No', 'No'),
                                                    ('Yes', 'Yes')],
                                           verbose_name="Written Safety Plan")
    optimizing_equipment = models.CharField(max_length=20, blank=True, null=True,
                                            choices=[('No', 'No'),
                                                     ('Yes', 'Yes')],
                                            verbose_name="Optimizing equipment")
    optimizing_equipment_description = models.TextField(null=True, blank=True,
                                                        verbose_name="Optimizing equipment (describe)")
    dust_collection_system = models.CharField(max_length=20, blank=True, null=True,
                                              choices=[('No', 'No'),
                                                       ('Yes', 'Yes')],
                                              verbose_name="Dust collection system")
    dust_collection_system_description = models.TextField(null=True, blank=True,
                                                          verbose_name="Dust collection system (describe)")
    housekeeping = models.CharField(max_length=20, blank=True, null=True,
                                    choices=[('No', 'No'), 
                                             ('Yes', 'Yes')],
                                    verbose_name="Housekeeping program in place and enforced  ")
    lock_out_tag = models.CharField(max_length=20, blank=True, null=True,
                                    choices=[('No', 'No'), ('Yes', 'Yes')],
                                    verbose_name="Lock Out Tag Out program for equipment maintenance")
    ppe_enforcement = models.CharField(max_length=20, blank=True, null=True,
                                       choices=[('No', 'No'), ('Yes', 'Yes')],
                                       verbose_name="Provides and enforces use of PPE")
    drug_alcohol_testing = models.CharField(max_length=20, blank=True, null=True,
                                            choices=[('No', 'No'),
                                                     ('Yes', 'Yes')],
                                            verbose_name="Drug and Alcohol testing program in place")
    new_employee_training = models.CharField(max_length=20, blank=True, null=True,
                                             choices=[('No', 'No'),
                                                      ('Yes', 'Yes')],
                                             verbose_name="New employee training program")
    vehicle_equipment_maintenance_plan = models.CharField(max_length=20, blank=True, null=True,
                                                          choices=[
                                                              ('No', 'No'), ('Yes', 'Yes')],
                                                          verbose_name="Written vehicle and equipment maintenance plan")
    first_aid_training = models.CharField(max_length=20, blank=True, null=True,
                                               choices=[('No', 'No'),
                                                        ('Yes', 'Yes')],
                                               verbose_name="Employees trained in first aid and CPR")
    bilingual_communication = models.CharField(max_length=20, blank=True, null=True,
                                               choices=[('No', 'No'),
                                                        ('Yes', 'Yes')],
                                               verbose_name="Bi-lingual communication capability, if needed")
    flammables_properly_stored = models.CharField(max_length=20, blank=True, null=True,
                                                  choices=[
                                                      ('No', 'No'), ('Yes', 'Yes')],
                                                  verbose_name="Enforces proper storage and use of flammables")
    pricing_comments = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class MechanicalCategories(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    cutting_operations = models.CharField(max_length=100, blank=True, null=True,
                                          choices=[('FAA Optimizing saws, mechanical sorting, lock out tag out', 'FAA Optimizing saws, mechanical sorting, lock out tag out'),
                                                   ('AA Mechanical sorting, guards, lock out tag out enforced',
                                                    'AA Mechanical sorting, guards, lock out tag out enforced'),
                                                   ('A Partially mechanical sorting, Log out tag out, guards',
                                                    'A Partially mechanical sorting, Log out tag out, guards'),
                                                   ('BA All manual sorting, informal lock out tag out', 'BA All manual sorting, informal lock out tag out')],
                                          verbose_name="Cutting Operations")
    dust_collection = models.CharField(max_length=100, blank=True, null=True,
                                       choices=[('FAA Dust Collection system, superior housekeeping', 'FAA Dust Collection system, superior housekeeping'),
                                                ('FAA Dust Collection system, superior housekeeping',
                                                 'FAA Dust Collection system, superior housekeeping'),
                                                ('AA Superior housekeeping, management enforces',
                                                 'AA Superior housekeeping, management enforces'),
                                                ('A Housekeeping program in place',
                                                 'A Housekeeping program in place'),
                                                ('BA No dust collection or housekeeping program', 'BA No dust collection or housekeeping program'), ],
                                       verbose_name="Dust Collection")
    forklift_usage = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA Training in place, no losses in past 3 years', 'FAA Training in place, no losses in past 3 years'),
                                               ('AA Training in place, minor losses in past 3 years',
                                                'AA Training in place, minor losses in past 3 years'),
                                               ('A No training or losses in past 3 years',
                                                'A No training or losses in past 3 years'),
                                               ('BA No training and losses in past 3 years', 'BA No training and losses in past 3 years'), ],
                                      verbose_name="Forklift Usage (if applicable)")
    losses_past_3yrs = models.CharField(max_length=100, blank=True, null=True,
                                        choices=[('FAA No Losses', 'FAA No Losses'),
                                                 ('AA Loss ratio < 30% w/o auto related WC claims',
                                                  'AA Loss ratio < 30% w/o auto related WC claims'),
                                                 ('A Loss ratio < 50% or related WC claims',
                                                  'A Loss ratio < 50% or related WC claims'),
                                                 ('BA Loss ratio > 50% or claims from uninsured subs', 'BA Loss ratio > 50% or claims from uninsured subs')],
                                        verbose_name="Losses past 3 years")
    business_experience = models.CharField(max_length=100, blank=True, null=True,
                                           choices=[('FAA >10 years continuous in industry', 'FAA >10 years continuous in industry'),
                                                    ('AA 6 to 10 years continuous in industry',
                                                     'AA 6 to 10 years continuous in industry'),
                                                    ('A 3 to 5 years continuous in industry',
                                                     'A 3 to 5 years continuous in industry'),
                                                    ('BA <3 years continuous in industry', 'BA <3 years continuous in industry')])
    cdl_auto_exposure = models.CharField(max_length=100, blank=True, null=True,
                                         choices=[('FAA No exposure or 100% insured subcontractors', 'FAA No exposure or 100% insured subcontractors'),
                                                  ('AA Owned autos insurred and subcontractors',
                                                   'AA Owned autos insurred and subcontractors'),
                                                  ('A 100% owned autos',
                                                   'A 100% owned autos'),
                                                  ('BA Any use of uninsured subcontractors', 'BA Any use of uninsured subcontractors')],
                                         verbose_name="CDL Auto Exposure (if applicable)")
    owned_auto_driver_experience = models.CharField(max_length=100, blank=True, null=True,
                                                    choices=[('FAA 75% CDL 5 years experience', 'FAA 75% CDL 5 years experience'),
                                                             ('AA 60% of CDL 5 years experience',
                                                              'AA 60% of CDL 5 years experience'),
                                                             ('A 40% of CDL 5 years experience',
                                                              'A 40% of CDL 5 years experience'),
                                                             ('BA <40% of CDL 5 years experience', 'BA <40% of CDL 5 years experience')],
                                                    verbose_name="Owned Auto - driver's experience")
    owned_auto_mvr = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA 60% CDL clear <10% borderline', 'FAA 60% CDL clear <10% borderline'),
                                               ('AA 50% to 59% CDL clear <10% borderline',
                                                'AA 50% to 59% CDL clear <10% borderline'),
                                               ('A 40% to 49% CDL clear <10% borderline',
                                                'A 40% to 49% CDL clear <10% borderline'),
                                               ('BA <40% CDL clear and / or >10% borderline', 'BA <40% CDL clear and / or >10% borderline')],
                                      verbose_name="Owned Auto - MVR's")
    safety = models.CharField(max_length=100, blank=True, null=True,
                              choices=[('FAA very proactive, anticipates hazards and formal plan in place', 'FAA very proactive, anticipates hazards and formal plan in place'),
                                       ('AA Established policies in plance and active management',
                                        'AA Established policies in plance and active management'),
                                       ('A Aware of major exposures and information plan in place',
                                        'A Aware of major exposures and information plan in place'),
                                       ('BA Management not actively involved and no plan', 'BA Management not actively involved and no plan')])
    loss_handling_and_trends = models.CharField(max_length=100, blank=True, null=True,
                                                choices=[('FAA Management has influence and loss results reflect', 'FAA Management has influence and loss results reflect'),
                                                         ('AA Management taking action, review of losses',
                                                          'AA Management taking action, review of losses'),
                                                         ('A Management addresses on a reactive basis',
                                                          'A Management addresses on a reactive basis'),
                                                         ('BA Management casually aware, ineffective approach', 'BA Management casually aware, ineffective approach')],
                                                verbose_name="Loss Handling & Trends")
    employee_turnover = models.CharField(max_length=100, blank=True, null=True,
                                         choices=[('FAA low turnover, stable, experienced <10%', 'FAA low turnover, stable, experienced <10%'),
                                                  ('AA low turnover, stable, experience <15%',
                                                   'AA low turnover, stable, experience <15%'),
                                                  ('A average turnover up to 20%',
                                                   'A average turnover up to 20%'),
                                                  ('BA below average turnover >20% turnover rate', 'BA below average turnover >20% turnover rate')],
                                         verbose_name="Employee Turnover")
    subcontracting = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA no exposure', 'FAA no exposure'),
                                               ('AA written program with exposure',
                                                'AA written program with exposure'),
                                               ('A no program, requires certificate of insurance',
                                                'A no program, requires certificate of insurance'),
                                               ('BA no program with uninsured subcontractors', 'BA no program with uninsured subcontractors')],
                                      verbose_name="Sub-Contracting")
    financial = models.CharField(max_length=100, blank=True, null=True,
                                 choices=[('Not included at this time', 'Not included at this time')], default='Not included at this time',
                                 verbose_name="Financial")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

"""
Underwriter Special Notes (Wood Manual)
"""

class WoodManualHeader(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    waiver_subrogation = models.CharField(max_length=20, blank=True, null=True,
                                          choices=[
                                              ('N/A', 'N/A'), ('Blanket', 'Blanket'), ('Specific', 'Specific')],
                                          verbose_name="Waiver of Subrogation")
    officers = models.CharField(max_length=20, blank=True, null=True,
                                choices=[('N/A', 'N/A'), ('Included',
                                                          'Included'), ('Excluded', 'Excluded')],
                                verbose_name="Officers - included/excluded")
    individual_partners = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[
                                               ('N/A', 'N/A'), ('Included', 'Included'), ('Excluded', 'Excluded')],
                                           verbose_name="Individual/Partners - included/excluded")
    mia_paid_reports_on_time = models.CharField(max_length=20, blank=True, null=True,
                                                choices=[
                                                    ('No', 'No'), ('Yes', 'Yes')],
                                                verbose_name="MIA Paid Monthly Reports on time")

    """Safety Programs, MFG Equipment and Operational Procedures"""
    written_safety_plan = models.CharField(max_length=20, blank=True, null=True,
                                           choices=[('No', 'No'),
                                                    ('Yes', 'Yes')],
                                           verbose_name="Written Safety Plan")
    management_routine_inspections = models.CharField(max_length=20, blank=True, null=True,
                                                      choices=[
                                                          ('No', 'No'), ('Yes', 'Yes')],
                                                      verbose_name="Management conducts routine inspections of power hand tools")
    dust_free_work_environment = models.CharField(max_length=20, blank=True, null=True,
                                                  choices=[
                                                      ('No', 'No'), ('Yes', 'Yes')],
                                                  verbose_name="Clean dust free work environment, daily clean up schedule")
    machines_properly_guarded = models.CharField(max_length=20, blank=True, null=True,
                                                 choices=[
                                                     ('No', 'No'), ('Yes', 'Yes')],
                                                 verbose_name="Machines properly guarded")
    power_hand_tools_mfg_instructions = models.CharField(max_length=20, blank=True, null=True,
                                                         choices=[
                                                             ('No', 'No'), ('Yes', 'Yes')],
                                                         verbose_name="Operates power hand tools according to MFG instructions, routine inspections")
    lock_out_tag = models.CharField(max_length=20, blank=True, null=True,
                                    choices=[('No', 'No'), ('Yes', 'Yes')],
                                    verbose_name="Lock Out Tag Out program for equipment maintenance")
    ppe_enforcement = models.CharField(max_length=20, blank=True, null=True,
                                       choices=[('No', 'No'), ('Yes', 'Yes')],
                                       verbose_name="Provides and enforces use of PPE")
    drug_alcohol_testing = models.CharField(max_length=20, blank=True, null=True,
                                            choices=[('No', 'No'),
                                                     ('Yes', 'Yes')],
                                            verbose_name="Drug and alcohol testing program in place")
    new_employee_training = models.CharField(max_length=20, blank=True, null=True,
                                             choices=[('No', 'No'),
                                                      ('Yes', 'Yes')],
                                             verbose_name="New employee training program")
    vehicle_equipment_maintenance_plan = models.CharField(max_length=20, blank=True, null=True,
                                                          choices=[
                                                              ('No', 'No'), ('Yes', 'Yes')],
                                                          verbose_name="Written vehicle and equipment maintenance plan")
    first_aid_training = models.CharField(max_length=20, blank=True, null=True,
                                          choices=[('No', 'No'),
                                                   ('Yes', 'Yes')],
                                          verbose_name="Employees trained in first aid and CPR")
    bilingual_communication = models.CharField(max_length=20, blank=True, null=True,
                                               choices=[('No', 'No'),
                                                        ('Yes', 'Yes')],
                                               verbose_name="Bi-lingual communication capability, if needed")
    flammables_properly_stored = models.CharField(max_length=20, blank=True, null=True,
                                                  choices=[
                                                      ('No', 'No'), ('Yes', 'Yes')],
                                                  verbose_name="Enforces proper storage and use of flammables")
    pricing_comments = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class WoodMechanicalCategories(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    operations_housekeeping = models.CharField(max_length=70, blank=True, null=True,
                                               choices=[('FAA Superior housekeeping program, enforced by management', 'FAA Superior housekeeping program, enforced by management'),
                                                        ('AA Housekeeiping program in place. Clean workspace',
                                                         'AA Housekeeiping program in place. Clean workspace'),
                                                        ('A Housekeeping program in place. Some accumulation',
                                                         'A Housekeeping program in place. Some accumulation'),
                                                        ('BA No formal housekeeping program.', 'BA No formal housekeeping program.')],
                                               verbose_name="Operations - housekeeping")
    forklift_usage = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA Training in place, no losses in past 3 years', 'FAA Training in place, no losses in past 3 years'),
                                               ('AA Training in place, minor losses in past 3 years',
                                                'AA Training in place, minor losses in past 3 years'),
                                               ('A No training or losses in past 3 years',
                                                'A No training or losses in past 3 years'),
                                               ('BA No training and losses in past 3 years', 'BA No training and losses in past 3 years'), ],
                                      verbose_name="Forklift usage (if applicable)")
    losses_past_3yrs = models.CharField(max_length=100, blank=True, null=True,
                                        choices=[('FAA No Losses', 'FAA No Losses'),
                                                 ('AA Loss ratio < 30% w/o auto related WC claims',
                                                  'AA Loss ratio < 30% w/o auto related WC claims'),
                                                 ('A Loss ratio < 50% or related WC claims',
                                                  'A Loss ratio < 50% or related WC claims'),
                                                 ('BA Loss ratio > 50% or claims from uninsured subs', 'BA Loss ratio > 50% or claims from uninsured subs')],
                                        verbose_name="Losses past 3 years")
    business_experience = models.CharField(max_length=100, blank=True, null=True,
                                           choices=[('FAA >10 years continuous in industry', 'FAA >10 years continuous in industry'),
                                                    ('AA 6 to 10 years continuous in industry',
                                                     'AA 6 to 10 years continuous in industry'),
                                                    ('A 3 to 5 years continuous in industry',
                                                     'A 3 to 5 years continuous in industry'),
                                                    ('BA <3 years continuous in industry', 'BA <3 years continuous in industry')],
                                           verbose_name="Business Experience")
    cdl_auto_exposure = models.CharField(max_length=100, blank=True, null=True,
                                         choices=[('FAA No exposure or 100% insured subcontractors', 'FAA No exposure or 100% insured subcontractors'),
                                                  ('AA Owned autos insurred and subcontractors',
                                                   'AA Owned autos insurred and subcontractors'),
                                                  ('A 100% owned autos',
                                                   'A 100% owned autos'),
                                                  ('BA Any use of uninsured subcontractors', 'BA Any use of uninsured subcontractors')],
                                         verbose_name="CDL Auto Exposure (if applicable)")
    owned_auto_driver_experience = models.CharField(max_length=100, blank=True, null=True,
                                                    choices=[('FAA 75% CDL 5 years experience', 'FAA 75% CDL 5 years experience'),
                                                             ('AA 60% of CDL 5 years experience',
                                                              'AA 60% of CDL 5 years experience'),
                                                             ('A 40% of CDL 5 years experience',
                                                              'A 40% of CDL 5 years experience'),
                                                             ('BA <40% of CDL 5 years experience', 'BA <40% of CDL 5 years experience')],
                                                    verbose_name="Owned Auto - Driver's Experience")
    owned_auto_mvr = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA 60% CDL clear <10% borderline', 'FAA 60% CDL clear <10% borderline'),
                                               ('AA 50% to 59% CDL clear <10% borderline',
                                                'AA 50% to 59% CDL clear <10% borderline'),
                                               ('A 40% to 49% CDL clear <10% borderline',
                                                'A 40% to 49% CDL clear <10% borderline'),
                                               ('BA <40% CDL clear and / or >10% borderline', 'BA <40% CDL clear and / or >10% borderline')],
                                      verbose_name="Owned Auto - MVR's")
    safety = models.CharField(max_length=100, blank=True, null=True,
                              choices=[('FAA very proactive, anticipates hazards and formal plan in place', 'FAA very proactive, anticipates hazards and formal plan in place'),
                                       ('AA Established policies in plance and active management',
                                        'AA Established policies in plance and active management'),
                                       ('A Aware of major exposures and information plan in place',
                                        'A Aware of major exposures and information plan in place'),
                                       ('BA Management not actively involved and no plan', 'BA Management not actively involved and no plan')],
                              verbose_name="Safety")
    loss_handling_and_trends = models.CharField(max_length=100, blank=True, null=True,
                                                choices=[('FAA Management has influence and loss results reflect', 'FAA Management has influence and loss results reflect'),
                                                         ('AA Management taking action, review of losses',
                                                          'AA Management taking action, review of losses'),
                                                         ('A Management addresses on a reactive basis',
                                                          'A Management addresses on a reactive basis'),
                                                         ('BA Management casually aware, ineffective approach', 'BA Management casually aware, ineffective approach')],
                                                verbose_name="Loss Handling & Trends")
    employee_turnover = models.CharField(max_length=100, blank=True, null=True,
                                         choices=[('FAA low turnover, stable, experienced <10%', 'FAA low turnover, stable, experienced <10%'),
                                                  ('AA low turnover, stable, experience <15%',
                                                   'AA low turnover, stable, experience <15%'),
                                                  ('A average turnover up to 20%',
                                                   'A average turnover up to 20%'),
                                                  ('BA below average turnover >20% turnover rate', 'BA below average turnover >20% turnover rate')],
                                         verbose_name="Employee Turnover")
    subcontracting = models.CharField(max_length=100, blank=True, null=True,
                                      choices=[('FAA no exposure', 'FAA no exposure'),
                                               ('AA written program with exposure',
                                                'AA written program with exposure'),
                                               ('A no program, requires certificate of insurance',
                                                'A no program, requires certificate of insurance'),
                                               ('BA no program with uninsured subcontractors', 'BA no program with uninsured subcontractors')],
                                      verbose_name="Sub-Contracting")
    financial = models.CharField(max_length=100, blank=True, null=True,
                                 choices=[('Not included at this time', 'Not included at this time')], default='Not included at this time',
                                 verbose_name="Financial")
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)

class Score(models.Model):
    generalinfo = models.ForeignKey(GeneralInfo, on_delete=models.CASCADE)
    class_fit = models.IntegerField(null=True, blank=True)
    wages = models.IntegerField(null=True, blank=True)
    safety_and_controls = models.IntegerField(null=True, blank=True)
    management = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.CharField(max_length=10, null=True, blank=True,)
    last_modified_date = models.DateTimeField(auto_now=True)
