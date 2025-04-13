# admin.py
from django.contrib import admin
from .models import LicenseKey

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'organization_name', 'application_name', 'is_active', 'is_valid', 'expiry_date')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('organization_name', 'application_name', 'key')
    readonly_fields = ('key', 'issued_date', 'created_at')
    
    fieldsets = (
        ('License Information', {
            'fields': ('key', 'is_active', 'issued_date', 'expiry_date')
        }),
        ('Organization Information', {
            'fields': ('organization_name', 'organization_description')
        }),
        ('Application Information', {
            'fields': ('application_name', 'application_url')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )