from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.SRHeader)
admin.site.register(models.SRStates)
admin.site.register(models.StateLines)
admin.site.register(models.StateHeader)
admin.site.register(models.CAHeader)
admin.site.register(models.CALines)
admin.site.register(models.AdaptedStateHeader)
admin.site.register(models.AdaptedStateLines)
