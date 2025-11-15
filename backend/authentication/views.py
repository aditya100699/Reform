"""
Authentication views for Aadhaar-based authentication.
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from .services import AadhaarService, AuthenticationService
from .serializers import (
    AadhaarOTPRequestSerializer, AadhaarOTPVerifySerializer,
    PasswordSetSerializer, LoginSerializer, UserSerializer
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()
aadhaar_service = AadhaarService()
auth_service = AuthenticationService()


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_aadhaar_auth(request):
    """
    Initiate Aadhaar authentication by sending OTP.
    POST /api/v1/auth/aadhaar/initiate/
    """
    serializer = AadhaarOTPRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    aadhaar_number = data['aadhaar_number']
    mobile = data['mobile']
    
    try:
        result = aadhaar_service.send_otp(aadhaar_number, mobile)
        return Response({
            'success': True,
            'session_id': result['session_id'],
            'expires_in': result['expires_in'],
            'message': result['message']
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error initiating Aadhaar auth: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_aadhaar_otp(request):
    """
    Verify Aadhaar OTP and create/update user.
    POST /api/v1/auth/aadhaar/verify/
    """
    serializer = AadhaarOTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    session_id = data['session_id']
    otp = data['otp']
    email = data.get('email')
    
    try:
        # Get mobile from session before verification (session is deleted after verification)
        from django.core.cache import cache
        session_data = cache.get(f'aadhaar_session_backup:{session_id}')
        if not session_data:
            return Response({
                'success': False,
                'error': 'Session expired. Please start again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mobile = session_data.get('mobile')
        if not mobile:
            return Response({
                'success': False,
                'error': 'Mobile number not found in session.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        result = aadhaar_service.verify_otp(session_id, otp)
        ekyc_data = result['ekyc_data']
        
        # Create or update user
        user = auth_service.create_or_update_user_from_aadhaar(ekyc_data, mobile, email)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'requires_password': not user.has_usable_password()
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error verifying Aadhaar OTP: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to verify OTP. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_password(request):
    """
    Set password for user account.
    POST /api/v1/auth/password/set/
    """
    serializer = PasswordSetSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    password = serializer.validated_data['password']
    
    user.set_password(password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Password set successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with mobile and password.
    POST /api/v1/auth/login/
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    mobile = serializer.validated_data['mobile']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(mobile=mobile)
        
        if not user.check_password(password):
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Account is inactive'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return Response({
            'success': False,
            'error': 'Login failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user (blacklist refresh token).
    POST /api/v1/auth/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token.
    POST /api/v1/auth/token/refresh/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        return Response({
            'success': True,
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get current user profile.
    GET /api/v1/auth/me/
    """
    return Response({
        'success': True,
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)

