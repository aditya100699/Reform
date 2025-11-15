"""
URL configuration for authentication app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Aadhaar Authentication
    path('aadhaar/initiate/', views.initiate_aadhaar_auth, name='aadhaar-initiate'),
    path('aadhaar/verify/', views.verify_aadhaar_otp, name='aadhaar-verify'),
    
    # Password Management
    path('password/set/', views.set_password, name='password-set'),
    
    # Login/Logout
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Token Management
    path('token/refresh/', views.refresh_token, name='token-refresh'),
    
    # User Profile
    path('me/', views.me, name='me'),
]

