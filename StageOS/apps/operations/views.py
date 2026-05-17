from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from .models import FOHPlan, ShowDayChecklist, Incident
from .serializers import FOHPlanSerializer, ShowDayChecklistSerializer, IncidentSerializer
from .services import log_incident, set_foh_status, check_checklist_item


class FOHPlanViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FOHPlan.objects.select_related('operating_context')
    serializer_class = FOHPlanSerializer
    filterset_fields = ['status']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        updated = set_foh_status(self.get_object(), request.user, 'confirmed', request.data.get('comment', ''))
        return Response(FOHPlanSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        updated = set_foh_status(self.get_object(), request.user, 'closed', request.data.get('comment', ''))
        return Response(FOHPlanSerializer(updated, context={'request': request}).data)


class ShowDayChecklistViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ShowDayChecklist.objects.select_related('foh_plan', 'checked_by')
    serializer_class = ShowDayChecklistSerializer
    filterset_fields = ['foh_plan', 'is_checked']
    ordering = ['item']

    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        updated = check_checklist_item(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ShowDayChecklistSerializer(updated, context={'request': request}).data)


class IncidentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Incident.objects.select_related(
        'operating_context', 'foh_plan', 'reported_by',
    )
    serializer_class = IncidentSerializer
    filterset_fields = ['operating_context', 'incident_type', 'severity']
    ordering = ['-occurred_at']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        incident = log_incident(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = incident
