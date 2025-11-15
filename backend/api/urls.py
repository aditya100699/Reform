"""
URL configuration for API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'records', views.HealthRecordViewSet, basename='healthrecord')
router.register(r'providers', views.ProviderViewSet, basename='provider')
router.register(r'shares', views.DocumentShareViewSet, basename='documentshare')
router.register(r'policies', views.InsurancePolicyViewSet, basename='insurancepolicy')
router.register(r'claims', views.InsuranceClaimViewSet, basename='insuranceclaim')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]

