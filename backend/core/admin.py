"""
Admin configuration for core models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, HealthRecord, Provider, DocumentShare,
    InsurancePolicy, InsuranceClaim, Notification, AuditLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin."""
    list_display = ('mobile', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_verified', 'created_at')
    list_filter = ('user_type', 'is_active', 'is_verified', 'aadhaar_linked')
    search_fields = ('mobile', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'aadhaar_token', 'aadhaar_linked', 'aadhaar_linked_at',
                      'profile_picture', 'date_of_birth', 'gender', 'is_verified',
                      'token_version', 'mfa_enabled', 'mfa_secret')
        }),
    )


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    """Health record admin."""
    list_display = ('title', 'patient', 'category', 'record_date', 'provider_name', 'status', 'created_at')
    list_filter = ('category', 'status', 'record_date')
    search_fields = ('title', 'patient__mobile', 'patient__first_name', 'provider_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'record_date'


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Provider admin."""
    list_display = ('name', 'provider_type', 'registration_number', 'city', 'is_verified', 'is_active')
    list_filter = ('provider_type', 'is_verified', 'is_active', 'state', 'city')
    search_fields = ('name', 'registration_number', 'email', 'phone')


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    """Document share admin."""
    list_display = ('patient', 'provider', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'expires_at')
    search_fields = ('patient__mobile', 'provider__name')
    filter_horizontal = ('records',)


@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    """Insurance policy admin."""
    list_display = ('policy_number', 'patient', 'insurance_company', 'coverage_amount', 'used_amount', 'status', 'end_date')
    list_filter = ('status', 'insurance_company', 'end_date')
    search_fields = ('policy_number', 'patient__mobile', 'insurance_company')


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    """Insurance claim admin."""
    list_display = ('claim_number', 'patient', 'policy', 'claimed_amount', 'approved_amount', 'status', 'claim_date')
    list_filter = ('status', 'claim_date')
    search_fields = ('claim_number', 'patient__mobile', 'policy__policy_number')
    filter_horizontal = ('supporting_documents',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""
    list_display = ('user', 'type', 'title', 'is_read', 'is_important', 'created_at')
    list_filter = ('type', 'is_read', 'is_important', 'created_at')
    search_fields = ('user__mobile', 'title', 'message')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log admin."""
    list_display = ('user', 'action', 'entity_type', 'ip_address', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('user__mobile', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

