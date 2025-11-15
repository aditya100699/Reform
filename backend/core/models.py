"""
Core models for Reform application.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import hashlib
import hmac
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager."""
    
    def create_user(self, mobile, password=None, **extra_fields):
        """Create and save a regular user."""
        if not mobile:
            raise ValueError('Mobile number is required')
        
        user = self.model(mobile=mobile, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, mobile, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', User.UserType.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(mobile, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with Aadhaar support."""
    
    class UserType(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        PROVIDER_ADMIN = 'PROVIDER_ADMIN', 'Provider Admin'
        PROVIDER_DOCTOR = 'PROVIDER_DOCTOR', 'Provider Doctor'
        PROVIDER_LAB_TECH = 'PROVIDER_LAB_TECH', 'Lab Technician'
        INSURANCE_OFFICER = 'INSURANCE_OFFICER', 'Insurance Officer'
        ADMIN = 'ADMIN', 'Admin'
    
    # Basic Information
    mobile = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # Aadhaar (tokenized, never store raw)
    aadhaar_token = models.CharField(max_length=128, unique=True, db_index=True, blank=True, null=True)
    aadhaar_linked = models.BooleanField(default=False)
    aadhaar_linked_at = models.DateTimeField(null=True, blank=True)
    
    # User Type
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.PATIENT)
    
    # Profile
    profile_picture = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Security
    token_version = models.IntegerField(default=1)  # For token revocation
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['mobile']),
            models.Index(fields=['aadhaar_token']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.mobile})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.mobile
    
    def get_short_name(self):
        return self.first_name or self.mobile
    
    @staticmethod
    def generate_aadhaar_token(aadhaar_number):
        """Generate irreversible token from Aadhaar number."""
        pepper = settings.AADHAAR_PEPPER
        token = hmac.new(
            pepper.encode(),
            aadhaar_number.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"atk_{token}"


class HealthRecord(models.Model):
    """Health records/documents model."""
    
    class RecordCategory(models.TextChoices):
        LAB_REPORT = 'LAB_REPORT', 'Lab Report'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription'
        IMAGING = 'IMAGING', 'Imaging/Scan'
        DISCHARGE_SUMMARY = 'DISCHARGE_SUMMARY', 'Discharge Summary'
        VACCINATION = 'VACCINATION', 'Vaccination Record'
        CONSULTATION = 'CONSULTATION', 'Consultation Notes'
        OTHER = 'OTHER', 'Other'
    
    class RecordStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Processing'
        PROCESSED = 'PROCESSED', 'Processed'
        ERROR = 'ERROR', 'Processing Error'
    
    # Ownership
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_records')
    
    # Document Info
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=RecordCategory.choices)
    description = models.TextField(blank=True)
    
    # File Storage
    file_url = models.URLField()  # S3 URL
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    file_type = models.CharField(max_length=50)  # MIME type
    
    # Metadata
    record_date = models.DateField()  # Date of the medical record
    provider_name = models.CharField(max_length=255, blank=True)  # Hospital/Clinic name
    provider_id = models.ForeignKey('Provider', on_delete=models.SET_NULL, null=True, blank=True)
    doctor_name = models.CharField(max_length=255, blank=True)
    
    # Processing
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.PENDING)
    ocr_data = models.JSONField(default=dict, blank=True)  # Extracted text/data
    extracted_values = models.JSONField(default=dict, blank=True)  # Structured data (test results, etc.)
    
    # Organization
    tags = models.JSONField(default=list, blank=True)  # User-defined tags
    notes = models.TextField(blank=True)  # User notes
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'health_records'
        ordering = ['-record_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', '-record_date']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['provider_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"


class Provider(models.Model):
    """Healthcare provider (hospital, clinic, lab) model."""
    
    class ProviderType(models.TextChoices):
        HOSPITAL = 'HOSPITAL', 'Hospital'
        CLINIC = 'CLINIC', 'Clinic'
        LAB = 'LAB', 'Laboratory'
        DIAGNOSTIC = 'DIAGNOSTIC', 'Diagnostic Center'
        PHARMACY = 'PHARMACY', 'Pharmacy'
    
    # Basic Info
    name = models.CharField(max_length=255)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    registration_number = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Admin
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_providers')
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'providers'
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['city', 'state']),
        ]
    
    def __str__(self):
        return self.name


class DocumentShare(models.Model):
    """Document sharing/consent model."""
    
    class ShareStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        GRANTED = 'GRANTED', 'Granted'
        REVOKED = 'REVOKED', 'Revoked'
        EXPIRED = 'EXPIRED', 'Expired'
    
    # Participants
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='received_shares')
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='shares_created')
    
    # Documents
    records = models.ManyToManyField(HealthRecord, related_name='shares')
    
    # Access Control
    status = models.CharField(max_length=20, choices=ShareStatus.choices, default=ShareStatus.PENDING)
    purpose = models.TextField()  # Reason for sharing
    granted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    allow_download = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_shares'
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} → {self.provider.name}"


class InsurancePolicy(models.Model):
    """Insurance policy model."""
    
    class PolicyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    # Ownership
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_policies')
    
    # Policy Info
    policy_number = models.CharField(max_length=100, db_index=True)
    insurance_company = models.CharField(max_length=255)
    policy_type = models.CharField(max_length=100)
    
    # Coverage
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    used_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=PolicyStatus.choices, default=PolicyStatus.ACTIVE)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'insurance_policies'
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['policy_number']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.insurance_company} - {self.policy_number}"
    
    @property
    def remaining_amount(self):
        return self.coverage_amount - self.used_amount
    
    @property
    def usage_percentage(self):
        if self.coverage_amount > 0:
            return (self.used_amount / self.coverage_amount) * 100
        return 0


class InsuranceClaim(models.Model):
    """Insurance claim model."""
    
    class ClaimStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PAYMENT_INITIATED = 'PAYMENT_INITIATED', 'Payment Initiated'
        PAID = 'PAID', 'Paid'
    
    # Ownership
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_claims')
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name='claims')
    
    # Claim Info
    claim_number = models.CharField(max_length=100, unique=True, db_index=True)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)
    
    # Amounts
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Documents
    supporting_documents = models.ManyToManyField(HealthRecord, related_name='claims')
    
    # Status
    status = models.CharField(max_length=20, choices=ClaimStatus.choices, default=ClaimStatus.PENDING)
    rejection_reason = models.TextField(blank=True)
    
    # Dates
    claim_date = models.DateField()
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'insurance_claims'
        ordering = ['-claim_date']
        indexes = [
            models.Index(fields=['patient', '-claim_date']),
            models.Index(fields=['policy', 'status']),
            models.Index(fields=['claim_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.claim_number} - {self.claimed_amount}"


class Notification(models.Model):
    """Notification model."""
    
    class NotificationType(models.TextChoices):
        RECORD_UPLOADED = 'RECORD_UPLOADED', 'Record Uploaded'
        RECORD_SHARED = 'RECORD_SHARED', 'Record Shared'
        CONSENT_REQUEST = 'CONSENT_REQUEST', 'Consent Request'
        CONSENT_GRANTED = 'CONSENT_GRANTED', 'Consent Granted'
        CLAIM_STATUS = 'CLAIM_STATUS', 'Claim Status Update'
        APPOINTMENT = 'APPOINTMENT', 'Appointment Reminder'
        MEDICATION = 'MEDICATION', 'Medication Reminder'
        TEST_RESULT = 'TEST_RESULT', 'Test Result Ready'
        OTHER = 'OTHER', 'Other'
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Content
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Additional data
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_important = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class AuditLog(models.Model):
    """Audit log for security and compliance."""
    
    class ActionType(models.TextChoices):
        LOGIN = 'LOGIN', 'User Login'
        LOGOUT = 'LOGOUT', 'User Logout'
        RECORD_VIEW = 'RECORD_VIEW', 'Record Viewed'
        RECORD_UPLOAD = 'RECORD_UPLOAD', 'Record Uploaded'
        RECORD_DELETE = 'RECORD_DELETE', 'Record Deleted'
        DOCUMENT_SHARE = 'DOCUMENT_SHARE', 'Document Shared'
        CONSENT_GRANTED = 'CONSENT_GRANTED', 'Consent Granted'
        CONSENT_REVOKED = 'CONSENT_REVOKED', 'Consent Revoked'
        AADHAAR_AUTH = 'AADHAAR_AUTH', 'Aadhaar Authentication'
        PASSWORD_CHANGE = 'PASSWORD_CHANGE', 'Password Changed'
        PROFILE_UPDATE = 'PROFILE_UPDATE', 'Profile Updated'
        OTHER = 'OTHER', 'Other'
    
    # User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    
    # Action
    action = models.CharField(max_length=30, choices=ActionType.choices)
    entity_type = models.CharField(max_length=50, blank=True)  # e.g., 'HealthRecord', 'DocumentShare'
    entity_id = models.CharField(max_length=100, blank=True)
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.user} - {self.created_at}"

