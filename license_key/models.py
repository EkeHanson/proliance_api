# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class LicenseKey(models.Model):
    # License Information
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    
    # Organization Information
    organization_name = models.CharField(max_length=255)
    organization_description = models.TextField(blank=True)
    
    # Application Information
    application_name = models.CharField(max_length=255)
    application_url = models.URLField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "License Key"
        verbose_name_plural = "License Keys"
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"{self.organization_name} - {self.application_name} ({self.key})"
    
    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Set expiry date to 1 year from issued date if not set
    #     if not self.expiry_date and self.issued_date:
    #         self.expiry_date = self.issued_date + timedelta(days=365)
    #     super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        """Check if license is currently valid"""
        now = timezone.now()
        return self.is_active and self.expiry_date > now