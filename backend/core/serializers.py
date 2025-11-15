"""
Serializers for core models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    HealthRecord, Provider, DocumentShare,
    InsurancePolicy, InsuranceClaim, Notification
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'mobile', 'email', 'first_name', 'last_name', 'full_name',
                 'user_type', 'profile_picture', 'date_of_birth', 'gender',
                 'aadhaar_linked', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'aadhaar_linked', 'is_verified')
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class HealthRecordSerializer(serializers.ModelSerializer):
    """Health record serializer."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    provider_name_display = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = ('id', 'title', 'category', 'description', 'file_url', 'file_name',
                 'file_size', 'file_type', 'record_date', 'provider_name', 'provider_id',
                 'provider_name_display', 'doctor_name', 'status', 'ocr_data',
                 'extracted_values', 'tags', 'notes', 'patient', 'patient_name',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'status', 'ocr_data', 'extracted_values')
    
    def validate_record_date(self, value):
        """Validate record date is not in the future."""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Record date cannot be in the future.")
        return value


class ProviderSerializer(serializers.ModelSerializer):
    """Provider serializer."""
    class Meta:
        model = Provider
        fields = ('id', 'name', 'provider_type', 'registration_number', 'email',
                 'phone', 'address', 'city', 'state', 'pincode', 'is_verified',
                 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified')


class DocumentShareSerializer(serializers.ModelSerializer):
    """Document share serializer."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    record_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentShare
        fields = ('id', 'patient', 'patient_name', 'provider', 'provider_name',
                 'records', 'record_count', 'status', 'purpose', 'granted_at',
                 'expires_at', 'allow_download', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'granted_at', 'status')
    
    def get_record_count(self, obj):
        return obj.records.count()


class InsurancePolicySerializer(serializers.ModelSerializer):
    """Insurance policy serializer."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    usage_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = InsurancePolicy
        fields = ('id', 'patient', 'patient_name', 'policy_number', 'insurance_company',
                 'policy_type', 'coverage_amount', 'used_amount', 'remaining_amount',
                 'usage_percentage', 'start_date', 'end_date', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'used_amount')


class InsuranceClaimSerializer(serializers.ModelSerializer):
    """Insurance claim serializer."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = InsuranceClaim
        fields = ('id', 'patient', 'patient_name', 'policy', 'policy_number',
                 'claim_number', 'provider', 'provider_name', 'claimed_amount',
                 'approved_amount', 'supporting_documents', 'status', 'rejection_reason',
                 'claim_date', 'approved_at', 'paid_at', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'claim_number',
                          'approved_amount', 'approved_at', 'paid_at', 'status')


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer."""
    class Meta:
        model = Notification
        fields = ('id', 'type', 'title', 'message', 'data', 'is_read',
                 'read_at', 'is_important', 'created_at')
        read_only_fields = ('id', 'created_at', 'read_at')

