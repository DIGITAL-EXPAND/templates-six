from django.db import models as db_models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views import TenantScopedMixin
from common.permissions import UserRoles, is_admin_user, user_type
from apps.structure.models import UserDepartmentMembership
from .models import FOHPlan, ShowDayChecklist, Incident, ShowCall, PostShowReport, StaffCall
from .serializers import (
    FOHPlanSerializer, ShowDayChecklistSerializer, IncidentSerializer,
    ShowCallSerializer, PostShowReportSerializer, StaffCallSerializer,
)
from .services import log_incident, set_foh_status, check_checklist_item


class FOHPlanViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FOHPlan.objects.select_related('operating_context')
    serializer_class = FOHPlanSerializer
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE}:
            return qs
        dept_ids = list(
            UserDepartmentMembership.objects.filter(user=user).values_list('department_id', flat=True)
        )
        return qs.filter(
            db_models.Q(operating_context__department_id__in=dept_ids)
            | db_models.Q(operating_context__department__isnull=True)
        )

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        user = self.request.user
        if not is_admin_user(user) and user_type(user) not in {UserRoles.EXECUTIVE}:
            context = serializer.validated_data.get('operating_context')
            if context and context.department_id:
                is_member = UserDepartmentMembership.objects.filter(
                    user=user, department_id=context.department_id
                ).exists()
                if not is_member:
                    raise PermissionDenied('You can only create FOH plans for your own department.')
        serializer.save(organisation_id=user.organisation_id)

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

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_admin_user(user) or user_type(user) in {UserRoles.EXECUTIVE}:
            return qs
        dept_ids = list(
            UserDepartmentMembership.objects.filter(user=user).values_list('department_id', flat=True)
        )
        return qs.filter(
            db_models.Q(operating_context__department_id__in=dept_ids)
            | db_models.Q(operating_context__department__isnull=True)
        )

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        incident = log_incident(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = incident


class ShowCallViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ShowCall.objects.select_related('operating_context', 'performance', 'created_by')
    serializer_class = ShowCallSerializer
    filterset_fields = ['operating_context', 'performance', 'status', 'show_date']
    ordering = ['-show_date', '-call_time']

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            created_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def distribute(self, request, pk=None):
        from django.utils import timezone
        show_call = self.get_object()
        show_call.status = 'distributed'
        show_call.distributed_at = timezone.now()
        show_call.save(update_fields=['status', 'distributed_at', 'updated_at'])
        return Response(ShowCallSerializer(show_call, context={'request': request}).data)


class PostShowReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = PostShowReport.objects.select_related('operating_context', 'performance', 'submitted_by')
    serializer_class = PostShowReportSerializer
    filterset_fields = ['operating_context', 'performance', 'show_date']
    ordering = ['-show_date']

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            submitted_by=self.request.user,
        )


class StaffCallViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = StaffCall.objects.select_related('show_call', 'staff_member')
    serializer_class = StaffCallSerializer
    filterset_fields = ['show_call', 'staff_member', 'role', 'status']
    ordering = ['call_time', 'role']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        from django.utils import timezone
        staff_call = self.get_object()
        staff_call.status = 'confirmed'
        staff_call.confirmed_at = timezone.now()
        staff_call.save(update_fields=['status', 'confirmed_at', 'updated_at'])
        return Response(StaffCallSerializer(staff_call, context={'request': request}).data)


# ── Liquor Licence & Safety Compliance ───────────────────────────────────────

from .models import LiquorLicence, SafetyComplianceRecord  # noqa: E402
from .serializers import LiquorLicenceSerializer, SafetyComplianceRecordSerializer  # noqa: E402


class LiquorLicenceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = LiquorLicence.objects.select_related('venue')
    serializer_class = LiquorLicenceSerializer
    filterset_fields = ['venue', 'status']
    search_fields = ['licence_number', 'licence_holder', 'issuing_authority']
    ordering = ['venue', 'status']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class SafetyComplianceRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SafetyComplianceRecord.objects.select_related('venue', 'operating_context', 'responsible_person')
    serializer_class = SafetyComplianceRecordSerializer
    filterset_fields = ['venue', 'operating_context', 'compliance_type', 'is_compliant']
    search_fields = ['certificate_number', 'issuing_body', 'notes']
    ordering = ['compliance_type', 'expiry_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


# ── Union Agreements ──────────────────────────────────────────────────────────

from .models import UnionAgreement, UnionCallRate, CrewCallUnionCheck  # noqa: E402
from .serializers import (  # noqa: E402
    UnionAgreementSerializer, UnionCallRateSerializer, CrewCallUnionCheckSerializer,
)


class UnionAgreementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = UnionAgreement.objects.prefetch_related('rates')
    serializer_class = UnionAgreementSerializer
    filterset_fields = ['union', 'is_active']
    search_fields = ['agreement_name']
    ordering = ['union', 'agreement_name']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def check_call(self, request, pk=None):
        """Check compliance of a call against this union agreement."""
        agreement = self.get_object()
        hours = float(request.data.get('hours', 0))
        role_category = request.data.get('role_category', '')

        minimum_call_met = hours >= float(agreement.minimum_call_hours)

        # Find applicable rate
        applicable_rate = UnionCallRate.objects.filter(
            agreement=agreement,
            role_category__iexact=role_category,
            organisation_id=request.user.organisation_id,
        ).first()

        estimated_cost = 0
        if applicable_rate:
            estimated_cost = float(applicable_rate.minimum_rate)
            if hours > float(agreement.overtime_threshold_hours):
                overtime_hours = hours - float(agreement.overtime_threshold_hours)
                hourly = float(applicable_rate.minimum_rate) / 8
                estimated_cost += overtime_hours * hourly * float(agreement.overtime_multiplier)

        return Response({
            'agreement_id': str(agreement.id),
            'agreement_name': agreement.agreement_name,
            'union': agreement.union,
            'hours_requested': hours,
            'minimum_call_hours': float(agreement.minimum_call_hours),
            'minimum_call_met': minimum_call_met,
            'turnaround_hours': float(agreement.turnaround_hours),
            'role_category': role_category,
            'applicable_rate': UnionCallRateSerializer(applicable_rate).data if applicable_rate else None,
            'estimated_cost': round(estimated_cost, 2),
            'compliance_issues': [] if minimum_call_met else [
                f'Call of {hours}h is below the minimum {agreement.minimum_call_hours}h call.'
            ],
        })


class UnionCallRateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = UnionCallRate.objects.select_related('agreement')
    serializer_class = UnionCallRateSerializer
    filterset_fields = ['agreement', 'rate_type']
    search_fields = ['role_category']
    ordering = ['agreement', 'role_category', 'rate_type']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class CrewCallUnionCheckViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = CrewCallUnionCheck.objects.select_related('staff_call', 'union_agreement', 'applicable_rate')
    serializer_class = CrewCallUnionCheckSerializer
    filterset_fields = ['staff_call', 'union_agreement', 'minimum_call_met', 'turnaround_met']
    ordering = ['-checked_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
