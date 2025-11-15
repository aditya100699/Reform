"""
Serializers for authentication.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .services import AadhaarService

User = get_user_model()
aadhaar_service = AadhaarService()


class AadhaarOTPRequestSerializer(serializers.Serializer):
    """Serializer for Aadhaar OTP request."""
    aadhaar_number = serializers.CharField(max_length=14, required=True)
    mobile = serializers.CharField(max_length=15, required=True)
    
    def validate_aadhaar_number(self, value):
        """Validate Aadhaar format."""
        if not aadhaar_service.validate_aadhaar_format(value):
            raise serializers.ValidationError("Invalid Aadhaar number format. Expected 12 digits.")
        return aadhaar_service.format_aadhaar(value)
    
    def validate_mobile(self, value):
        """Validate mobile number format."""
        import re
        # Remove +91 prefix if present
        cleaned = value.replace('+91', '').strip()
        if not re.match(r'^\d{10}$', cleaned):
            raise serializers.ValidationError("Invalid mobile number format. Expected 10 digits.")
        return f"+91{cleaned}"


class AadhaarOTPVerifySerializer(serializers.Serializer):
    """Serializer for Aadhaar OTP verification."""
    session_id = serializers.CharField(max_length=100, required=True)
    otp = serializers.CharField(max_length=6, min_length=6, required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    
    def validate_otp(self, value):
        """Validate OTP format."""
        import re
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("OTP must be 6 digits.")
        return value


class PasswordSetSerializer(serializers.Serializer):
    """Serializer for setting password."""
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate_password(self, value):
        """Validate password strength."""
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for login."""
    mobile = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate_mobile(self, value):
        """Validate mobile number format."""
        import re
        cleaned = value.replace('+91', '').strip()
        if not re.match(r'^\d{10}$', cleaned):
            raise serializers.ValidationError("Invalid mobile number format.")
        return f"+91{cleaned}"


class UserSerializer(serializers.ModelSerializer):
    """User serializer for authentication responses."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'mobile', 'email', 'first_name', 'last_name', 'full_name',
                 'user_type', 'profile_picture', 'date_of_birth', 'gender',
                 'aadhaar_linked', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'aadhaar_linked', 'is_verified')
    
    def get_full_name(self, obj):
        return obj.get_full_name()

