"""
Authentication services for Aadhaar-based authentication.
"""
import re
import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
import requests
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AadhaarService:
    """Service for Aadhaar authentication."""
    
    def __init__(self):
        self.license_key = settings.UIDAI_LICENSE_KEY
        self.aua_code = settings.UIDAI_AUA_CODE
        self.sub_aua_code = settings.UIDAI_SUB_AUA_CODE
        # In production, this would be the actual UIDAI API endpoint
        self.base_url = getattr(settings, 'UIDAI_API_URL', 'https://authgateway.uidai.gov.in')
    
    @staticmethod
    def validate_aadhaar_format(aadhaar_number):
        """Validate Aadhaar number format (12 digits)."""
        # Remove hyphens and spaces
        cleaned = re.sub(r'[-\s]', '', aadhaar_number)
        # Check if it's 12 digits
        return bool(re.match(r'^\d{12}$', cleaned))
    
    @staticmethod
    def format_aadhaar(aadhaar_number):
        """Format Aadhaar number as XXXX-XXXX-XXXX."""
        cleaned = re.sub(r'[-\s]', '', aadhaar_number)
        if len(cleaned) == 12:
            return f"{cleaned[:4]}-{cleaned[4:8]}-{cleaned[8:]}"
        return aadhaar_number
    
    def send_otp(self, aadhaar_number, mobile):
        """
        Send OTP to mobile number via UIDAI API.
        In production, this would call the actual UIDAI API.
        """
        if not self.validate_aadhaar_format(aadhaar_number):
            raise ValueError("Invalid Aadhaar format")
        
        # Generate session ID
        session_id = hashlib.sha256(
            f"{aadhaar_number}{mobile}{timezone.now().isoformat()}".encode()
        ).hexdigest()[:32]
        
        session_data = {
            'aadhaar': aadhaar_number,
            'mobile': mobile,
            'timestamp': timezone.now().isoformat(),
        }
        
        # Store session in cache (5 minutes TTL)
        cache.set(
            f'aadhaar_session:{session_id}',
            session_data,
            timeout=300  # 5 minutes
        )
        # Also store backup for verification
        cache.set(
            f'aadhaar_session_backup:{session_id}',
            session_data,
            timeout=300  # 5 minutes
        )
        
        # In production, make actual API call:
        # response = requests.post(
        #     f"{self.base_url}/otp/send",
        #     json={
        #         'aadhaar': aadhaar_number,
        #         'mobile': mobile,
        #         'licenseKey': self.license_key,
        #         'auaCode': self.aua_code,
        #     },
        #     headers={'Content-Type': 'application/json'},
        #     verify=True
        # )
        
        # For development, return mock response
        logger.info(f"OTP sent to {mobile} for Aadhaar ending in {aadhaar_number[-4:]}")
        
        return {
            'session_id': session_id,
            'expires_in': 300,
            'message': 'OTP sent successfully'
        }
    
    def verify_otp(self, session_id, otp):
        """
        Verify OTP with UIDAI API.
        In production, this would call the actual UIDAI API.
        """
        # Retrieve session
        session_data = cache.get(f'aadhaar_session:{session_id}')
        if not session_data:
            raise ValueError("Session expired or invalid")
        
        # In production, verify with UIDAI:
        # response = requests.post(
        #     f"{self.base_url}/otp/verify",
        #     json={
        #         'sessionId': session_id,
        #         'otp': otp,
        #         'licenseKey': self.license_key,
        #     },
        #     verify=True
        # )
        
        # For development, accept any 6-digit OTP
        if not re.match(r'^\d{6}$', otp):
            raise ValueError("Invalid OTP format")
        
        # Mock verification - in production, check UIDAI response
        is_valid = True  # Replace with actual UIDAI response check
        
        if not is_valid:
            logger.warning(f"Failed OTP verification attempt for session {session_id}")
            raise ValueError("Invalid OTP")
        
        # Get eKYC data (in production, call UIDAI eKYC API)
        ekyc_data = self.get_ekyc(session_id)
        
        # Clear session
        cache.delete(f'aadhaar_session:{session_id}')
        
        return {
            'verified': True,
            'ekyc_data': ekyc_data
        }
    
    def get_ekyc(self, session_id):
        """
        Get eKYC data from UIDAI.
        In production, this would call the actual UIDAI eKYC API.
        """
        session_data = cache.get(f'aadhaar_session:{session_id}')
        if not session_data:
            raise ValueError("Session expired")
        
        # In production, call UIDAI eKYC API:
        # response = requests.post(
        #     f"{self.base_url}/ekyc",
        #     json={
        #         'sessionId': session_id,
        #         'licenseKey': self.license_key,
        #     },
        #     verify=True
        # )
        
        # Mock eKYC data for development
        return {
            'aadhaar': session_data['aadhaar'],
            'name': 'Mock User Name',  # Would come from UIDAI
            'dob': '1990-01-01',  # Would come from UIDAI
            'gender': 'M',  # Would come from UIDAI
            'address': 'Mock Address',  # Would come from UIDAI
        }


class AuthenticationService:
    """Service for user authentication."""
    
    @staticmethod
    def create_or_update_user_from_aadhaar(ekyc_data, mobile, email=None):
        """Create or update user from Aadhaar eKYC data."""
        aadhaar_token = User.generate_aadhaar_token(ekyc_data['aadhaar'])
        
        # Try to find existing user by Aadhaar token
        user = User.objects.filter(aadhaar_token=aadhaar_token).first()
        
        if user:
            # Update existing user
            user.mobile = mobile
            if email:
                user.email = email
            user.aadhaar_linked = True
            user.aadhaar_linked_at = timezone.now()
            user.first_name = ekyc_data.get('name', '').split()[0] if ekyc_data.get('name') else ''
            user.last_name = ' '.join(ekyc_data.get('name', '').split()[1:]) if ekyc_data.get('name') else ''
            if ekyc_data.get('dob'):
                from datetime import datetime
                try:
                    user.date_of_birth = datetime.strptime(ekyc_data['dob'], '%Y-%m-%d').date()
                except:
                    pass
            user.gender = ekyc_data.get('gender', '')
            user.is_verified = True
            user.save()
        else:
            # Check if user exists with mobile
            user = User.objects.filter(mobile=mobile).first()
            
            if user:
                # Link Aadhaar to existing user
                user.aadhaar_token = aadhaar_token
                user.aadhaar_linked = True
                user.aadhaar_linked_at = timezone.now()
                user.is_verified = True
                user.save()
            else:
                # Create new user
                user = User.objects.create_user(
                    mobile=mobile,
                    email=email,
                    aadhaar_token=aadhaar_token,
                    aadhaar_linked=True,
                    aadhaar_linked_at=timezone.now(),
                    first_name=ekyc_data.get('name', '').split()[0] if ekyc_data.get('name') else '',
                    last_name=' '.join(ekyc_data.get('name', '').split()[1:]) if ekyc_data.get('name') else '',
                    date_of_birth=datetime.strptime(ekyc_data['dob'], '%Y-%m-%d').date() if ekyc_data.get('dob') else None,
                    gender=ekyc_data.get('gender', ''),
                    is_verified=True,
                    user_type=User.UserType.PATIENT
                )
        
        return user

