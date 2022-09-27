from rest_framework import serializers
from .models import GeneralInfo


class GeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralInfo
        fields = ('id', 'unique_number', 'named_insured', 'dba', 'uw', 'term', 'state', 'agent_number', 
                'agency_name', 'effective_date', 'account_number', 'expiration_date')
