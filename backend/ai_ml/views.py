"""
API views for AI/ML features.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import HealthInsight, HealthTrend, HealthRisk
from .serializers import HealthInsightSerializer, HealthTrendSerializer, HealthRiskSerializer
from .services import HealthAnalyzer, PredictiveModel
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class HealthTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for health trends."""
    serializer_class = HealthTrendSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['metric_name']
    
    def get_queryset(self):
        """Return trends for the current user."""
        return HealthTrend.objects.filter(patient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze health records and generate trends."""
        analyzer = HealthAnalyzer(request.user)
        metric_name = request.data.get('metric_name')  # Optional
        
        try:
            trends = analyzer.analyze_trends(metric_name=metric_name)
            serializer = self.get_serializer(trends, many=True)
            return Response({
                'success': True,
                'trends': serializer.data,
                'count': len(trends)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def predict(self, request, pk=None):
        """Predict future values for a trend."""
        trend = self.get_object()
        days_ahead = int(request.query_params.get('days_ahead', 90))
        
        try:
            predictions = PredictiveModel.predict_future_values(
                request.user,
                trend.metric_name,
                days_ahead=days_ahead
            )
            
            if predictions:
                return Response({
                    'success': True,
                    'metric_name': trend.metric_name,
                    'predictions': predictions
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Not enough data for prediction'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error predicting future values: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthRiskViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for health risks."""
    serializer_class = HealthRiskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'risk_level']
    
    def get_queryset(self):
        """Return risks for the current user."""
        return HealthRisk.objects.filter(patient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def assess(self, request):
        """Assess health risks."""
        analyzer = HealthAnalyzer(request.user)
        
        try:
            risks = analyzer.assess_health_risks()
            serializer = self.get_serializer(risks, many=True)
            return Response({
                'success': True,
                'risks': serializer.data,
                'count': len(risks)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthInsightViewSet(viewsets.ModelViewSet):
    """ViewSet for health insights."""
    serializer_class = HealthInsightSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'severity', 'is_active']
    
    def get_queryset(self):
        """Return insights for the current user."""
        return HealthInsight.objects.filter(patient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate comprehensive health insights."""
        analyzer = HealthAnalyzer(request.user)
        
        try:
            insights = analyzer.generate_insights()
            serializer = self.get_serializer(insights, many=True)
            return Response({
                'success': True,
                'insights': serializer.data,
                'count': len(insights)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def detect_anomalies(self, request):
        """Detect anomalies in health records."""
        analyzer = HealthAnalyzer(request.user)
        
        try:
            anomalies = analyzer.detect_anomalies()
            return Response({
                'success': True,
                'anomalies': anomalies,
                'count': len(anomalies)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

