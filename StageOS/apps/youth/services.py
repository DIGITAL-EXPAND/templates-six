from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Count, Q
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditEvent
from apps.audit.services import AuditService

_VALID_YOUTH_CONTEXT_TYPES = {'youth_project', 'festival'}


def create_youth_project(context, user, data):
    from .models import YouthProject
    if context.context_type not in _VALID_YOUTH_CONTEXT_TYPES:
        raise ValidationError(
            {'detail': 'Youth projects must be linked to a YOUTH_PROJECT or FESTIVAL context'}
        )
    project = YouthProject.objects.create(
        organisation=context.organisation,
        operating_context=context,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='YOUTH_PROJECT_CREATED',
        payload={
            'project_id': str(project.id),
            'context_id': str(context.id),
            'context_type': context.context_type,
        },
    )
    return project


@transaction.atomic
def capture_session_attendance(session, user, attendance_data):
    from .models import AttendanceRecord
    if session.status in ('completed', 'cancelled'):
        raise ValidationError(
            {'detail': f'Cannot capture attendance for a {session.status} session'}
        )

    records = []
    for entry in attendance_data:
        learner_id = entry['learner_identifier']
        record, _ = AttendanceRecord.objects.update_or_create(
            session=session,
            learner_identifier=learner_id,
            defaults={
                'organisation': session.organisation,
                'present': entry.get('present', False),
                'notes': entry.get('notes', ''),
            },
        )
        records.append(record)

    session.attendance_captured = True
    session.status = 'completed'
    session.save(update_fields=['attendance_captured', 'status', 'updated_at'])

    total_present = sum(1 for e in attendance_data if e.get('present', False))
    total_absent = len(attendance_data) - total_present

    AuditEvent.objects.create(
        organisation=session.organisation,
        actor=user,
        event_type='ATTENDANCE_CAPTURED',
        payload={
            'session_id': str(session.id),
            'total_present': total_present,
            'total_absent': total_absent,
            'total_learners': len(attendance_data),
        },
    )
    return records


def get_project_stats(youth_project):
    from .models import Activity, Session, AttendanceRecord, ConsentRecord, ShowcaseOutput

    activities_qs = Activity.objects.filter(youth_project=youth_project)
    activity_count = activities_qs.count()

    sessions_qs = Session.objects.filter(activity__youth_project=youth_project)
    total_sessions = sessions_qs.count()
    completed_sessions = sessions_qs.filter(status='completed').count()

    consent_qs = ConsentRecord.objects.filter(youth_project=youth_project)
    total_consent = consent_qs.count()
    consented = consent_qs.filter(guardian_consent_received=True).count()
    consent_rate = round((consented / total_consent * 100), 1) if total_consent > 0 else 0.0

    attendance_qs = AttendanceRecord.objects.filter(
        session__activity__youth_project=youth_project,
    )
    unique_learners = attendance_qs.values('learner_identifier').distinct().count()

    # Average attendance rate across completed sessions
    completed_session_ids = list(
        sessions_qs.filter(status='completed').values_list('id', flat=True)
    )
    avg_attendance_rate = 0.0
    if completed_session_ids:
        rates = []
        for sid in completed_session_ids:
            records = AttendanceRecord.objects.filter(session_id=sid)
            total = records.count()
            if total > 0:
                present = records.filter(present=True).count()
                rates.append(present / total * 100)
        avg_attendance_rate = round(sum(rates) / len(rates), 1) if rates else 0.0

    showcase_count = ShowcaseOutput.objects.filter(youth_project=youth_project).count()

    return {
        'activity_count': activity_count,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_consent_records': total_consent,
        'consented_learners': consented,
        'consent_rate': consent_rate,
        'unique_learners_attended': unique_learners,
        'avg_attendance_rate': avg_attendance_rate,
        'showcase_output_count': showcase_count,
    }


def set_youth_project_status(project, user, status, comment=''):
    old_status = project.status
    project.status = status
    project.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=project.organisation,
        actor=user,
        event_type='YOUTH_PROJECT_STATUS_CHANGED',
        target_type='YouthProject',
        target_id=project.id,
        old_value=old_status,
        new_value=status,
        reason=comment,
    )
    return project


def receive_consent(consent, user, comment=''):
    old_value = consent.guardian_consent_received
    consent.guardian_consent_received = True
    consent.consent_date = timezone.now().date()
    consent.withdrawal_date = None
    consent.save(update_fields=[
        'guardian_consent_received', 'consent_date', 'withdrawal_date', 'updated_at',
    ])
    AuditService.record(
        organisation=consent.organisation,
        actor=user,
        event_type='YOUTH_CONSENT_RECEIVED',
        target_type='ConsentRecord',
        target_id=consent.id,
        old_value=old_value,
        new_value=True,
        reason=comment,
    )
    return consent


def withdraw_consent(consent, user, comment=''):
    if consent.consent_date and timezone.now().date() < consent.consent_date:
        raise ValidationError({'detail': 'Withdrawal date cannot be before consent date.'})
    old_value = consent.withdrawal_date
    consent.withdrawal_date = timezone.now().date()
    consent.guardian_consent_received = False
    consent.save(update_fields=['withdrawal_date', 'guardian_consent_received', 'updated_at'])
    AuditService.record(
        organisation=consent.organisation,
        actor=user,
        event_type='YOUTH_CONSENT_WITHDRAWN',
        target_type='ConsentRecord',
        target_id=consent.id,
        old_value=old_value or '',
        new_value=consent.withdrawal_date,
        reason=comment,
    )
    return consent


def vet_facilitator(assignment, user, comment=''):
    old_value = assignment.is_vetted
    assignment.is_vetted = True
    assignment.vetting_date = timezone.now().date()
    assignment.save(update_fields=['is_vetted', 'vetting_date', 'updated_at'])
    AuditService.record(
        organisation=assignment.organisation,
        actor=user,
        event_type='FACILITATOR_VETTED',
        target_type='FacilitatorAssignment',
        target_id=assignment.id,
        old_value=old_value,
        new_value=True,
        reason=comment,
    )
    return assignment


def complete_session(session, user, comment=''):
    if not session.attendance_captured:
        raise ValidationError({
            'detail': 'Attendance must be captured before a youth session can be completed.'
        })
    old_status = session.status
    session.status = 'completed'
    session.save(update_fields=['status', 'updated_at'])
    AuditService.record(
        organisation=session.organisation,
        actor=user,
        event_type='YOUTH_SESSION_COMPLETED',
        target_type='Session',
        target_id=session.id,
        old_value=old_status,
        new_value=session.status,
        reason=comment,
    )
    return session
