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


# ── Maintenance & Facilities ──────────────────────────────────────────────────

from .models import (  # noqa: E402
    MaintenanceTicket, MaintenanceSchedule, InspectionRecord, VenueDowntime,
    AudienceComplaint, AccessibilityRequirement, LateSeatingPolicy,
)
from .serializers import (  # noqa: E402
    MaintenanceTicketSerializer, MaintenanceScheduleSerializer,
    InspectionRecordSerializer, VenueDowntimeSerializer,
    AudienceComplaintSerializer, AccessibilityRequirementSerializer,
    LateSeatingPolicySerializer,
)


class MaintenanceTicketViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = MaintenanceTicket.objects.select_related(
        'venue', 'affected_production', 'reported_by', 'assigned_to',
    )
    serializer_class = MaintenanceTicketSerializer
    filterset_fields = ['status', 'priority', 'category', 'venue', 'is_production_impacting']
    search_fields = ['title', 'ticket_number', 'description', 'location_detail']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            reported_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        from django.contrib.auth import get_user_model
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'user_id': 'This field is required.'})
        User = get_user_model()
        assignee = User.objects.filter(id=user_id, organisation_id=request.user.organisation_id).first()
        if not assignee:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'user_id': 'User not found in your organisation.'})
        ticket.assigned_to = assignee
        ticket.status = 'assigned'
        ticket.save(update_fields=['assigned_to', 'status', 'updated_at'])
        return Response(MaintenanceTicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        import datetime
        ticket = self.get_object()
        ticket.resolution_notes = request.data.get('resolution_notes', '')
        ticket.status = 'resolved'
        ticket.resolved_date = datetime.date.today()
        ticket.save(update_fields=['resolution_notes', 'status', 'resolved_date', 'updated_at'])
        return Response(MaintenanceTicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'escalated'
        ticket.priority = 'critical'
        ticket.save(update_fields=['status', 'priority', 'updated_at'])
        return Response(MaintenanceTicketSerializer(ticket, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def kpis(self, request):
        import datetime
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        qs = self.get_queryset()
        open_statuses = ['logged', 'assigned', 'in_progress', 'awaiting_parts', 'escalated']
        total_open = qs.filter(status__in=open_statuses).count()
        critical_count = qs.filter(status__in=open_statuses, priority='critical').count()
        today = datetime.date.today()
        overdue_count = qs.filter(
            status__in=open_statuses,
            target_resolution_date__lt=today,
        ).count()
        production_impacting_count = qs.filter(
            status__in=open_statuses, is_production_impacting=True,
        ).count()
        resolved_qs = qs.filter(status__in=['resolved', 'closed'], resolved_date__isnull=False)
        avg_resolution_days = None
        if resolved_qs.exists():
            total_days = sum(
                (r.resolved_date - r.created_at.date()).days
                for r in resolved_qs
                if r.resolved_date and r.created_at
            )
            avg_resolution_days = round(total_days / resolved_qs.count(), 1)
        return Response({
            'total_open': total_open,
            'critical_count': critical_count,
            'overdue_count': overdue_count,
            'avg_resolution_days': avg_resolution_days,
            'production_impacting_count': production_impacting_count,
        })


class MaintenanceScheduleViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.select_related('venue', 'assigned_to')
    serializer_class = MaintenanceScheduleSerializer
    filterset_fields = ['venue', 'category', 'frequency', 'is_active']
    search_fields = ['title']
    ordering = ['next_due_date', 'title']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        import datetime
        from dateutil.relativedelta import relativedelta
        schedule = self.get_object()
        today = datetime.date.today()
        schedule.last_completed_date = today
        freq_map = {
            'daily': relativedelta(days=1),
            'weekly': relativedelta(weeks=1),
            'monthly': relativedelta(months=1),
            'quarterly': relativedelta(months=3),
            'biannual': relativedelta(months=6),
            'annual': relativedelta(years=1),
        }
        delta = freq_map.get(schedule.frequency)
        schedule.next_due_date = today + delta if delta else None
        schedule.save(update_fields=['last_completed_date', 'next_due_date'])
        return Response(MaintenanceScheduleSerializer(schedule, context={'request': request}).data)


class InspectionRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = InspectionRecord.objects.select_related('venue')
    serializer_class = InspectionRecordSerializer
    filterset_fields = ['venue', 'inspection_type', 'passed']
    search_fields = ['inspector_name', 'inspector_company', 'certificate_number']
    ordering = ['-inspection_date']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class VenueDowntimeViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = VenueDowntime.objects.select_related('venue', 'ticket')
    serializer_class = VenueDowntimeSerializer
    filterset_fields = ['venue', 'is_resolved']
    search_fields = ['reason']
    ordering = ['-start_datetime']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        from django.utils import timezone
        downtime = self.get_object()
        downtime.is_resolved = True
        downtime.end_datetime = timezone.now()
        downtime.save(update_fields=['is_resolved', 'end_datetime'])
        return Response(VenueDowntimeSerializer(downtime, context={'request': request}).data)


# ── Audience Complaints & Accessibility ───────────────────────────────────────

class AudienceComplaintViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AudienceComplaint.objects.select_related('operating_context', 'assigned_to')
    serializer_class = AudienceComplaintSerializer
    filterset_fields = ['status', 'category', 'operating_context', 'requires_follow_up']
    search_fields = ['reference_number', 'complainant_name', 'complainant_email', 'description']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        import datetime
        complaint = self.get_object()
        complaint.resolution = request.data.get('resolution', '')
        complaint.status = 'resolved'
        complaint.resolved_date = datetime.date.today()
        complaint.save(update_fields=['resolution', 'status', 'resolved_date', 'updated_at'])
        return Response(AudienceComplaintSerializer(complaint, context={'request': request}).data)


class AccessibilityRequirementViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AccessibilityRequirement.objects.select_related('operating_context', 'assigned_to')
    serializer_class = AccessibilityRequirementSerializer
    filterset_fields = ['operating_context', 'requirement_type', 'is_confirmed']
    search_fields = ['patron_name', 'patron_contact', 'details']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)


class LateSeatingPolicyViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = LateSeatingPolicy.objects.select_related('operating_context')
    serializer_class = LateSeatingPolicySerializer
    filterset_fields = ['operating_context', 'exceptions_allowed']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(organisation_id=self.request.user.organisation_id)
