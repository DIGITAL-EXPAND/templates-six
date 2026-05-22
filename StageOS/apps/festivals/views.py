from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from .models import Festival, FestivalVenue, FestivalPass, FestivalVenueSlot
from .serializers import (
    FestivalSerializer, FestivalVenueSerializer,
    FestivalPassSerializer, FestivalVenueSlotSerializer,
)


class FestivalViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Festival.objects.prefetch_related('venues', 'passes', 'venue_slots')
    serializer_class = FestivalSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'edition', 'artistic_director']
    ordering = ['-start_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Returns all venue slots for the festival organised by date then venue."""
        festival = self.get_object()
        slots = FestivalVenueSlot.objects.filter(
            festival=festival,
            organisation_id=request.user.organisation_id,
        ).select_related('festival_venue', 'festival_venue__venue', 'operating_context').order_by('slot_date', 'start_time')

        schedule = {}
        for slot in slots:
            date_str = str(slot.slot_date)
            venue_code = slot.festival_venue.venue_code or str(slot.festival_venue.venue_id)
            if date_str not in schedule:
                schedule[date_str] = {}
            if venue_code not in schedule[date_str]:
                schedule[date_str][venue_code] = []
            schedule[date_str][venue_code].append({
                'slot_id': str(slot.id),
                'start_time': str(slot.start_time),
                'end_time': str(slot.end_time),
                'slot_label': slot.slot_label,
                'is_confirmed': slot.is_confirmed,
                'operating_context': str(slot.operating_context_id) if slot.operating_context_id else None,
                'notes': slot.notes,
            })
        return Response({'festival_id': str(festival.id), 'schedule': schedule})

    @action(detail=True, methods=['get'])
    def accreditation_summary(self, request, pk=None):
        """Count passes by type and calculate % of max_accreditation used."""
        festival = self.get_object()
        passes = FestivalPass.objects.filter(
            festival=festival,
            organisation_id=request.user.organisation_id,
        )
        from django.db.models import Count
        by_type = passes.values('pass_type').annotate(count=Count('id'))
        total = passes.count()
        pct_used = (total / festival.max_accreditation * 100) if festival.max_accreditation else 0
        return Response({
            'festival_id': str(festival.id),
            'max_accreditation': festival.max_accreditation,
            'total_passes_issued': total,
            'percent_used': round(pct_used, 2),
            'by_type': list(by_type),
        })


class FestivalVenueViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FestivalVenue.objects.select_related('festival', 'venue')
    serializer_class = FestivalVenueSerializer
    filterset_fields = ['festival', 'venue', 'is_primary']
    ordering = ['festival', 'venue_code']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class FestivalPassViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FestivalPass.objects.select_related('festival')
    serializer_class = FestivalPassSerializer
    filterset_fields = ['festival', 'pass_type', 'is_active']
    search_fields = ['holder_name', 'holder_email', 'organisation_name', 'pass_number']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a festival pass."""
        festival_pass = self.get_object()
        festival_pass.is_active = True
        festival_pass.save(update_fields=['is_active'])
        return Response(FestivalPassSerializer(festival_pass, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a festival pass."""
        festival_pass = self.get_object()
        festival_pass.is_active = False
        festival_pass.save(update_fields=['is_active'])
        return Response(FestivalPassSerializer(festival_pass, context={'request': request}).data)


class FestivalVenueSlotViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FestivalVenueSlot.objects.select_related('festival', 'festival_venue', 'operating_context')
    serializer_class = FestivalVenueSlotSerializer
    filterset_fields = ['festival', 'festival_venue', 'slot_date', 'is_confirmed']
    ordering = ['slot_date', 'start_time']

    def get_queryset(self):
        qs = super().get_queryset()
        festival = self.request.query_params.get('festival')
        if festival:
            qs = qs.filter(festival_id=festival)
        slot_date = self.request.query_params.get('slot_date')
        if slot_date:
            qs = qs.filter(slot_date=slot_date)
        return qs

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
