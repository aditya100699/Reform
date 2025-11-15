"""
URL configuration for AI/ML app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'trends', views.HealthTrendViewSet, basename='healthtrend')
router.register(r'risks', views.HealthRiskViewSet, basename='healthrisk')
router.register(r'insights', views.HealthInsightViewSet, basename='healthinsight')

app_name = 'ai_ml'

urlpatterns = [
    path('', include(router.urls)),
]

