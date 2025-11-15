"""
Serializers for AI/ML models.
"""
from rest_framework import serializers
from .models import HealthInsight, HealthTrend, HealthRisk


class HealthTrendSerializer(serializers.ModelSerializer):
    """Serializer for health trends."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    
    class Meta:
        model = HealthTrend
        fields = ('id', 'patient', 'patient_name', 'metric_name', 'metric_unit',
                 'data_points', 'trend_direction', 'trend_strength', 'current_value',
                 'average_value', 'min_value', 'max_value', 'change_percentage',
                 'normal_range_min', 'normal_range_max', 'last_updated', 'created_at')
        read_only_fields = ('id', 'created_at', 'last_updated')


class HealthRiskSerializer(serializers.ModelSerializer):
    """Serializer for health risks."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    
    class Meta:
        model = HealthRisk
        fields = ('id', 'patient', 'patient_name', 'category', 'risk_score',
                 'risk_level', 'description', 'contributing_factors', 'recommendations',
                 'related_records', 'assessed_at', 'updated_at')
        read_only_fields = ('id', 'assessed_at', 'updated_at')


class HealthInsightSerializer(serializers.ModelSerializer):
    """Serializer for health insights."""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    
    class Meta:
        model = HealthInsight
        fields = ('id', 'patient', 'patient_name', 'type', 'title', 'description',
                 'severity', 'related_records', 'metrics', 'predictions', 'recommendations',
                 'confidence_score', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

