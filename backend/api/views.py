"""
API views for Reform application.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from core.models import (
    HealthRecord, Provider, DocumentShare,
    InsurancePolicy, InsuranceClaim, Notification
)
from core.serializers import (
    HealthRecordSerializer, ProviderSerializer, DocumentShareSerializer,
    InsurancePolicySerializer, InsuranceClaimSerializer, NotificationSerializer
)
from core.models import User
import logging

logger = logging.getLogger(__name__)


class HealthRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for health records."""
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'record_date']
    search_fields = ['title', 'description', 'provider_name', 'doctor_name']
    ordering_fields = ['record_date', 'created_at']
    ordering = ['-record_date', '-created_at']
    
    def get_queryset(self):
        """Return records for the current user."""
        user = self.request.user
        if user.user_type == User.UserType.PATIENT:
            return HealthRecord.objects.filter(patient=user)
        # For providers, return records they have access to via shares
        elif user.user_type in [User.UserType.PROVIDER_DOCTOR, User.UserType.PROVIDER_ADMIN]:
            # Get provider associated with user
            provider = Provider.objects.filter(admin_user=user).first()
            if provider:
                shares = DocumentShare.objects.filter(
                    provider=provider,
                    status=DocumentShare.ShareStatus.GRANTED
                )
                record_ids = []
                for share in shares:
                    record_ids.extend(share.records.values_list('id', flat=True))
                return HealthRecord.objects.filter(id__in=record_ids)
        return HealthRecord.objects.none()
    
    def perform_create(self, serializer):
        """Set patient and uploaded_by when creating record."""
        serializer.save(
            patient=self.request.user,
            uploaded_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a health record with a provider."""
        record = self.get_object()
        provider_id = request.data.get('provider_id')
        purpose = request.data.get('purpose', '')
        duration_days = int(request.data.get('duration_days', 30))
        allow_download = request.data.get('allow_download', False)
        
        if not provider_id:
            return Response({
                'success': False,
                'error': 'Provider ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from django.utils import timezone
        from datetime import timedelta
        
        share = DocumentShare.objects.create(
            patient=request.user,
            provider=provider,
            shared_by=request.user,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(days=duration_days),
            allow_download=allow_download,
            status=DocumentShare.ShareStatus.GRANTED
        )
        share.records.add(record)
        
        return Response({
            'success': True,
            'share': DocumentShareSerializer(share).data
        }, status=status.HTTP_201_CREATED)


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for healthcare providers."""
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider_type', 'city', 'state', 'is_verified']
    search_fields = ['name', 'city', 'state']
    
    def get_queryset(self):
        """Return verified and active providers."""
        return Provider.objects.filter(is_verified=True, is_active=True)


class DocumentShareViewSet(viewsets.ModelViewSet):
    """ViewSet for document shares."""
    serializer_class = DocumentShareSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'provider']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return shares for the current user."""
        user = self.request.user
        if user.user_type == User.UserType.PATIENT:
            return DocumentShare.objects.filter(patient=user)
        elif user.user_type in [User.UserType.PROVIDER_DOCTOR, User.UserType.PROVIDER_ADMIN]:
            provider = Provider.objects.filter(admin_user=user).first()
            if provider:
                return DocumentShare.objects.filter(provider=provider)
        return DocumentShare.objects.none()
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a document share."""
        share = self.get_object()
        if share.patient != request.user:
            return Response({
                'success': False,
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        share.status = DocumentShare.ShareStatus.REVOKED
        share.save()
        
        return Response({
            'success': True,
            'message': 'Share revoked successfully'
        })


class InsurancePolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for insurance policies."""
    serializer_class = InsurancePolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'insurance_company']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return policies for the current user."""
        user = self.request.user
        if user.user_type == User.UserType.PATIENT:
            return InsurancePolicy.objects.filter(patient=user)
        return InsurancePolicy.objects.none()
    
    def perform_create(self, serializer):
        """Set patient when creating policy."""
        serializer.save(patient=self.request.user)


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    """ViewSet for insurance claims."""
    serializer_class = InsuranceClaimSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'policy']
    ordering = ['-claim_date']
    
    def get_queryset(self):
        """Return claims for the current user."""
        user = self.request.user
        if user.user_type == User.UserType.PATIENT:
            return InsuranceClaim.objects.filter(patient=user)
        return InsuranceClaim.objects.none()
    
    def perform_create(self, serializer):
        """Set patient and generate claim number when creating claim."""
        import uuid
        claim_number = f"CLM{uuid.uuid4().hex[:10].upper()}"
        serializer.save(patient=self.request.user, claim_number=claim_number)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read', 'is_important']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        from django.utils import timezone
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': 'All notifications marked as read'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'success': True,
            'count': count
        })

