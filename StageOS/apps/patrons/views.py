from django.db import models
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views import TenantScopedMixin
from .models import Patron, PatronAttendance, PatronCommunication
from .serializers import PatronSerializer, PatronAttendanceSerializer, PatronCommunicationSerializer


class PatronViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Patron.objects.prefetch_related('attendances')
    serializer_class = PatronSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['segment', 'source', 'is_active', 'marketing_opt_in', 'popia_consent_given']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'city']
    ordering_fields = ['last_name', 'total_spend', 'total_bookings', 'last_visit_date', 'created_at']
    ordering = ['last_name', 'first_name']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        from django.db.models import Sum, Count, Avg
        qs = self.get_queryset()
        data = qs.aggregate(
            total=Count('id'),
            opted_in=Count('id', filter=models.Q(marketing_opt_in=True)),
            total_revenue=Sum('total_spend'),
            avg_spend=Avg('total_spend'),
        )
        by_segment = list(
            qs.values('segment').annotate(count=Count('id')).order_by('-count')
        )
        return Response({**data, 'by_segment': by_segment})


class PatronAttendanceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PatronAttendance.objects.select_related('patron', 'operating_context', 'performance')
    serializer_class = PatronAttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patron', 'operating_context', 'performance', 'is_comp', 'attendance_date']
    ordering = ['-attendance_date']


class PatronCommunicationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PatronCommunication.objects.select_related('patron', 'sent_by', 'operating_context')
    serializer_class = PatronCommunicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patron', 'operating_context', 'channel']
    ordering = ['-sent_at']
