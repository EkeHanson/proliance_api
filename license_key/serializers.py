# serializers.py
from rest_framework import serializers
from .models import LicenseKey
from datetime import datetime, timedelta
from django.utils import timezone

class LicenseKeySerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateTimeField(required=False)

    class Meta:
        model = LicenseKey
        fields = '__all__'
        read_only_fields = ('key', 'issued_date', 'created_at')

    def validate(self, data):
        # Ensure expiry date is in the future if provided
        expiry = data.get('expiry_date')
        if expiry and expiry < timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return data
