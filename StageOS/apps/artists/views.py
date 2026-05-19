from datetime import date

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from common.permissions import CanAccessArtistData, IsTenantMember, UserRoles, user_type
from .models import Artist, ArtistDocument, ArtistEngagement, ArtistPayment, PaymentStatus
from .serializers import (
    ArtistSerializer, ArtistDocumentSerializer, ArtistEngagementSerializer,
    ArtistPaymentSerializer,
)
from .services import (
    upload_artist_document, confirm_engagement,
    verify_artist_document, reject_artist_document,
)


class ArtistViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessArtistData]
    filterset_fields = ['status', 'discipline']
    search_fields = ['legal_name', 'professional_name']
    ordering = ['legal_name']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.ARTIST_EXTERNAL:
            return qs.filter(contact_email=self.request.user.email)
        return qs


class ArtistDocumentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ArtistDocument.objects.select_related('artist', 'document', 'verified_by')
    serializer_class = ArtistDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessArtistData]
    filterset_fields = ['artist', 'document_type', 'status']
    ordering = ['document_type']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.ARTIST_EXTERNAL:
            return qs.filter(artist__contact_email=self.request.user.email)
        return qs

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        updated = verify_artist_document(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ArtistDocumentSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        updated = reject_artist_document(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ArtistDocumentSerializer(updated, context={'request': request}).data)


class ArtistEngagementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ArtistEngagement.objects.select_related('artist', 'operating_context', 'contract')
    serializer_class = ArtistEngagementSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessArtistData]
    filterset_fields = ['artist', 'operating_context', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if user_type(self.request.user) == UserRoles.ARTIST_EXTERNAL:
            return qs.filter(artist__contact_email=self.request.user.email)
        return qs

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        engagement = self.get_object()
        updated = confirm_engagement(engagement, request.user)
        return Response(ArtistEngagementSerializer(updated, context={'request': request}).data)


class ArtistPaymentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ArtistPayment.objects.select_related('engagement', 'approved_by')
    serializer_class = ArtistPaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember, CanAccessArtistData]
    filterset_fields = ['engagement', 'milestone', 'status']
    ordering = ['due_date', 'created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        payment.status = PaymentStatus.APPROVED
        payment.approved_by = request.user
        payment.save(update_fields=['status', 'approved_by', 'updated_at'])
        return Response(ArtistPaymentSerializer(payment, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        payment = self.get_object()
        payment.status = PaymentStatus.PAID
        payment.paid_date = date.today()
        payment.save(update_fields=['status', 'paid_date', 'updated_at'])
        return Response(ArtistPaymentSerializer(payment, context={'request': request}).data)
