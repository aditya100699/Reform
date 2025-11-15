"""
Admin configuration for AI/ML models.
"""
from django.contrib import admin
from .models import HealthInsight, HealthTrend, HealthRisk


@admin.register(HealthInsight)
class HealthInsightAdmin(admin.ModelAdmin):
    """Health insight admin."""
    list_display = ('title', 'patient', 'type', 'severity', 'confidence_score', 'is_active', 'created_at')
    list_filter = ('type', 'severity', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'patient__mobile', 'patient__first_name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('related_records',)
    date_hierarchy = 'created_at'


@admin.register(HealthTrend)
class HealthTrendAdmin(admin.ModelAdmin):
    """Health trend admin."""
    list_display = ('metric_name', 'patient', 'trend_direction', 'current_value', 'change_percentage', 'last_updated')
    list_filter = ('trend_direction', 'metric_name')
    search_fields = ('metric_name', 'patient__mobile', 'patient__first_name')
    readonly_fields = ('last_updated', 'created_at')
    date_hierarchy = 'last_updated'


@admin.register(HealthRisk)
class HealthRiskAdmin(admin.ModelAdmin):
    """Health risk admin."""
    list_display = ('category', 'patient', 'risk_level', 'risk_score', 'assessed_at')
    list_filter = ('category', 'risk_level', 'assessed_at')
    search_fields = ('category', 'description', 'patient__mobile', 'patient__first_name')
    readonly_fields = ('assessed_at', 'updated_at')
    filter_horizontal = ('related_records',)
    date_hierarchy = 'assessed_at'

