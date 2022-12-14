from django.contrib import admin
from . import models

admin.site.register(models.GeneralInfo)
admin.site.register(models.GeneralInfoPremium)
admin.site.register(models.AccountHistory)
admin.site.register(models.LossRatingValuation)
admin.site.register(models.RiskHeader)
admin.site.register(models.RiskExmod)
admin.site.register(models.Checklist)
admin.site.register(models.Comments)
admin.site.register(models.Claims)
admin.site.register(models.EvalUnderwriter)
admin.site.register(models.WoodMechanicalCategories)
admin.site.register(models.WoodManualHeader)
admin.site.register(models.MechanicalCategories)
admin.site.register(models.MechanicalHeader)
admin.site.register(models.LoggingExposureCategories)
admin.site.register(models.LoggingHeader)
admin.site.register(models.Export)
admin.site.register(models.Upload)
admin.site.register(models.Score)