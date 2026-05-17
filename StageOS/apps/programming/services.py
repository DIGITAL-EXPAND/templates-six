from datetime import datetime, time, timedelta
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from apps.audit.models import AuditEvent
from common import department_permissions
from common.permissions import UserRoles, is_admin_user, user_type


class ConflictException(APIException):
    status_code = 409
    default_detail = 'A scheduling conflict exists.'
    default_code = 'conflict'


BLOCKING_SLOT_TYPES = {'maintenance', 'blackout', 'venue_unavailable', 'dark_day'}


def _is_programming_calendar_manager(user):
    if is_admin_user(user) or user_type(user) == UserRoles.EXECUTIVE:
        return True
    memberships = department_permissions.user_department_memberships(user)
    if not memberships.exists():
        return user_type(user) in {UserRoles.MANAGER, UserRoles.STAFF}
    return (
        memberships.filter(department__department_type='programming', can_manage_department=True).exists()
        or memberships.filter(authority_level='gm').exists()
    )


def require_programming_calendar_authority(user):
    if not _is_programming_calendar_manager(user):
        raise PermissionDenied('You cannot edit this venue hold because Programming owns venue scheduling.')


def _time_window(date_value, start_value, end_value, setup_minutes=0, strike_minutes=0):
    start = start_value or time(0, 0)
    end = end_value or time(23, 59, 59)
    start_dt = datetime.combine(date_value, start) - timedelta(minutes=setup_minutes or 0)
    end_dt = datetime.combine(date_value, end) + timedelta(minutes=strike_minutes or 0)
    if end_dt <= start_dt:
        raise ValidationError({'end_time': 'End time must be after start time.'})
    return start_dt, end_dt


def _overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def _conflict_issue(organisation, user, *, context=None, venue_hold=None, calendar_slot=None, title, description, severity='high'):
    from .models import CalendarIssue
    return CalendarIssue.objects.create(
        organisation=organisation,
        title=title,
        description=description,
        operating_context=context,
        venue_hold=venue_hold,
        calendar_slot=calendar_slot,
        severity=severity,
        raised_by=user,
    )


def _audit_calendar_block(organisation, user, payload):
    AuditEvent.objects.create(
        organisation=organisation,
        actor=user,
        event_type='calendar.conflict_blocked',
        target_type=payload.get('source_type', 'Calendar'),
        target_id=payload.get('source_id'),
        payload=payload,
    )


def _blocked_conflict(organisation, user, *, context, source_type, source_id, description, venue_hold=None, calendar_slot=None):
    issue = _conflict_issue(
        organisation,
        user,
        context=context,
        venue_hold=venue_hold,
        calendar_slot=calendar_slot,
        title='Calendar conflict blocked',
        description=description,
        severity='critical',
    )
    _audit_calendar_block(organisation, user, {
        'source_type': source_type,
        'source_id': str(source_id or issue.id),
        'issue_id': str(issue.id),
        'detail': description,
    })
    raise ConflictException(detail=description)


def _capacity_issue_if_needed(organisation, user, *, context, venue, expected_audience, source_type, venue_hold=None, calendar_slot=None):
    if not expected_audience or not getattr(venue, 'capacity', None) or expected_audience <= venue.capacity:
        return
    over_percent = ((expected_audience - venue.capacity) / venue.capacity) * 100
    description = f'Expected audience {expected_audience} exceeds {venue.name} capacity {venue.capacity}.'
    _conflict_issue(
        organisation,
        user,
        context=context,
        venue_hold=venue_hold,
        calendar_slot=calendar_slot,
        title='Venue capacity warning',
        description=description,
        severity='critical' if over_percent > 10 else 'high',
    )
    if over_percent > 10:
        _audit_calendar_block(organisation, user, {
            'source_type': source_type,
            'source_id': str(getattr(venue_hold or calendar_slot, 'id', '')),
            'detail': description,
        })
        raise ConflictException(detail=description)


def _validate_calendar_conflicts(organisation, user, *, context, venue, date_value, start_time, end_time,
                                 setup_buffer_minutes=0, strike_buffer_minutes=0, is_confirmed=False,
                                 is_blocking_slot=False, hold_type=None, source_hold=None, source_slot=None,
                                 expected_audience=None):
    from .models import CalendarSlot, HoldType, VenueHold

    new_start, new_end = _time_window(date_value, start_time, end_time, setup_buffer_minutes, strike_buffer_minutes)
    _capacity_issue_if_needed(
        organisation,
        user,
        context=context,
        venue=venue,
        expected_audience=expected_audience,
        source_type='VenueHold' if source_hold else 'CalendarSlot',
        venue_hold=source_hold,
        calendar_slot=source_slot,
    )

    for existing in VenueHold.objects.filter(organisation=organisation, venue=venue, hold_date=date_value).exclude(id=getattr(source_hold, 'id', None)):
        existing_start, existing_end = _time_window(
            existing.hold_date, existing.start_time, existing.end_time,
            existing.setup_buffer_minutes, existing.strike_buffer_minutes,
        )
        if not _overlaps(new_start, new_end, existing_start, existing_end):
            continue
        existing_confirmed = existing.hold_type in {HoldType.CONFIRMED, HoldType.BLOCKED}
        new_confirmed = is_confirmed or hold_type in {HoldType.CONFIRMED, HoldType.BLOCKED}
        description = (
            f'Time conflict with existing {existing.hold_type} hold '
            f'{existing.start_time or "00:00"}-{existing.end_time or "23:59"} at {venue.name}.'
        )
        if existing_confirmed or new_confirmed:
            _blocked_conflict(
                organisation, user, context=context, source_type='VenueHold',
                source_id=getattr(source_hold, 'id', None), description=description, venue_hold=existing,
            )
        _conflict_issue(
            organisation, user, context=context, venue_hold=existing,
            title='Provisional venue overlap warning', description=description, severity='medium',
        )

    for existing in CalendarSlot.objects.filter(organisation=organisation, venue=venue, date=date_value).exclude(id=getattr(source_slot, 'id', None)):
        existing_start, existing_end = _time_window(
            existing.date, existing.start_time, existing.end_time,
            existing.setup_buffer_minutes, existing.strike_buffer_minutes,
        )
        if not _overlaps(new_start, new_end, existing_start, existing_end):
            continue
        existing_confirmed = existing.is_confirmed or existing.slot_type in BLOCKING_SLOT_TYPES
        new_confirmed = is_confirmed or is_blocking_slot or hold_type in {HoldType.CONFIRMED, HoldType.BLOCKED}
        description = (
            f'Time conflict with existing {existing.slot_type} slot '
            f'{existing.start_time or "00:00"}-{existing.end_time or "23:59"} at {venue.name}.'
        )
        if existing_confirmed or new_confirmed:
            _blocked_conflict(
                organisation, user, context=context, source_type='CalendarSlot',
                source_id=getattr(source_slot, 'id', None), description=description, calendar_slot=existing,
            )
        _conflict_issue(
            organisation, user, context=context, calendar_slot=existing,
            title='Provisional calendar overlap warning', description=description, severity='medium',
        )


def create_intake_request(organisation, user, data):
    from .models import IntakeRequest

    request = IntakeRequest.objects.create(
        organisation=organisation,
        submitted_by=user if getattr(user, 'is_authenticated', False) else None,
        **data,
    )
    AuditEvent.objects.create(
        organisation=organisation,
        actor=user if getattr(user, 'is_authenticated', False) else None,
        event_type='intake.request_submitted',
        target_type='IntakeRequest',
        target_id=request.id,
        payload={
            'intake_request_id': str(request.id),
            'request_type': request.request_type,
            'event_title': request.event_title,
        },
    )
    return request


def mark_intake_under_review(intake_request, user, comment=''):
    from .models import IntakeRequestStatus

    if intake_request.status not in {
        IntakeRequestStatus.SUBMITTED,
        IntakeRequestStatus.CHANGES_REQUESTED,
        IntakeRequestStatus.DEFERRED,
    }:
        raise ValidationError({'detail': f"Cannot review an intake request in '{intake_request.status}' status."})
    old_status = intake_request.status
    intake_request.status = IntakeRequestStatus.UNDER_REVIEW
    intake_request.reviewed_by = user
    intake_request.decision_comment = comment
    intake_request.save(update_fields=['status', 'reviewed_by', 'decision_comment', 'updated_at'])
    _audit_intake_action(intake_request, user, 'intake.review_started', old_status, comment)
    return intake_request


def decide_intake_request(intake_request, user, status, comment=''):
    from django.utils import timezone
    from .models import IntakeRequestStatus

    if status in {IntakeRequestStatus.DECLINED, IntakeRequestStatus.CHANGES_REQUESTED} and not comment.strip():
        raise ValidationError({'comment': 'A comment is required for this decision.'})
    if intake_request.status == IntakeRequestStatus.CONVERTED:
        raise ValidationError({'detail': 'Converted intake requests cannot be decided again.'})
    if intake_request.status == IntakeRequestStatus.ARCHIVED:
        raise ValidationError({'detail': 'Archived intake requests cannot be decided.'})
    old_status = intake_request.status
    intake_request.status = status
    intake_request.decided_by = user
    intake_request.decision_comment = comment
    intake_request.decision_at = timezone.now()
    intake_request.save(update_fields=[
        'status', 'decided_by', 'decision_comment', 'decision_at', 'updated_at',
    ])
    _audit_intake_action(intake_request, user, f'intake.{status}', old_status, comment)
    return intake_request


def convert_intake_to_context(intake_request, user, data):
    from .models import IntakeRequestStatus
    from .serializers import REQUEST_TYPE_TO_CONTEXT_TYPE
    from apps.contexts.services import create_context

    if intake_request.status != IntakeRequestStatus.APPROVED:
        raise ValidationError({'detail': 'Only approved intake requests can be converted to a Workspace.'})
    if intake_request.converted_context_id:
        raise ValidationError({'detail': 'This intake request has already been converted.'})

    site = data.get('site')
    venue = data.get('venue') or intake_request.preferred_venue
    if not site and venue:
        site = venue.site
    if not site:
        raise ValidationError({'site': 'A site is required when the request has no preferred venue.'})

    context = create_context(
        organisation=intake_request.organisation,
        user=user,
        data={
            'title': intake_request.event_title,
            'context_type': REQUEST_TYPE_TO_CONTEXT_TYPE[intake_request.request_type].value,
            'site': site,
            'venue': venue,
            'owner': data['owner'],
            'department': data.get('department'),
            'priority': data.get('priority', 'medium'),
            'risk_level': data.get('risk_level', 'low'),
            'budget': data.get('budget', 0),
            'synopsis': intake_request.notes,
            'start_date': intake_request.requested_start_date,
            'end_date': intake_request.requested_end_date,
            'opening_date': intake_request.requested_start_date,
            'ticketing_provider': 'to_confirm' if intake_request.ticketing_required else '',
        },
    )

    old_status = intake_request.status
    intake_request.status = IntakeRequestStatus.CONVERTED
    intake_request.converted_context = context
    intake_request.save(update_fields=['status', 'converted_context', 'updated_at'])
    _audit_intake_action(
        intake_request,
        user,
        'intake.converted_to_workspace',
        old_status,
        f'Converted to Workspace {context.id}',
        {'context_id': str(context.id)},
    )
    return context


def _audit_intake_action(intake_request, user, event_type, old_status, comment='', extra_payload=None):
    payload = {
        'intake_request_id': str(intake_request.id),
        'old_status': old_status,
        'new_status': intake_request.status,
        'comment': comment,
    }
    if extra_payload:
        payload.update(extra_payload)
    AuditEvent.objects.create(
        organisation=intake_request.organisation,
        actor=user,
        event_type=event_type,
        target_type='IntakeRequest',
        target_id=intake_request.id,
        payload=payload,
    )


def assign_producer(context, producer, assigned_by, **kwargs):
    from .models import ProducerAssignment
    if ProducerAssignment.objects.filter(operating_context=context, producer=producer).exists():
        raise ValidationError({'detail': 'This producer is already assigned to this context.'})
    assignment = ProducerAssignment.objects.create(
        organisation=context.organisation,
        operating_context=context,
        producer=producer,
        assigned_by=assigned_by,
        **kwargs,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=assigned_by,
        event_type='producer.assigned',
        payload={
            'assignment_id': str(assignment.id),
            'context_id': str(context.id),
            'producer_id': str(producer.id),
            'is_primary': assignment.is_primary,
        },
    )
    return assignment


def create_venue_hold(context, user, data):
    from .models import VenueHold
    require_programming_calendar_authority(user)
    _validate_calendar_conflicts(
        organisation=context.organisation,
        user=user,
        context=context,
        venue=data.get('venue'),
        date_value=data.get('hold_date'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        setup_buffer_minutes=data.get('setup_buffer_minutes', 0),
        strike_buffer_minutes=data.get('strike_buffer_minutes', 0),
        hold_type=data.get('hold_type'),
        expected_audience=data.get('expected_audience'),
    )
    hold = VenueHold.objects.create(
        organisation=context.organisation,
        operating_context=context,
        held_by=user,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='venue_hold.created',
        payload={
            'hold_id': str(hold.id),
            'context_id': str(context.id),
            'venue_id': str(hold.venue_id),
            'hold_date': str(hold.hold_date),
        },
    )
    return hold


def update_venue_hold(hold, user, data):
    require_programming_calendar_authority(user)
    for key, value in data.items():
        setattr(hold, key, value)
    _validate_calendar_conflicts(
        hold.organisation,
        user,
        context=hold.operating_context,
        venue=hold.venue,
        date_value=hold.hold_date,
        start_time=hold.start_time,
        end_time=hold.end_time,
        setup_buffer_minutes=hold.setup_buffer_minutes,
        strike_buffer_minutes=hold.strike_buffer_minutes,
        hold_type=hold.hold_type,
        source_hold=hold,
        expected_audience=hold.expected_audience,
    )
    hold.save()
    return hold


def create_calendar_slot(context, user, data):
    from .models import CalendarSlot
    require_programming_calendar_authority(user)
    _validate_calendar_conflicts(
        context.organisation,
        user,
        context=context,
        venue=data.get('venue'),
        date_value=data.get('date'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        setup_buffer_minutes=data.get('setup_buffer_minutes', 0),
        strike_buffer_minutes=data.get('strike_buffer_minutes', 0),
        is_confirmed=data.get('is_confirmed', False),
        is_blocking_slot=data.get('slot_type') in BLOCKING_SLOT_TYPES,
        expected_audience=data.get('expected_audience'),
    )
    slot = CalendarSlot.objects.create(
        organisation=context.organisation,
        operating_context=context,
        **data,
    )
    AuditEvent.objects.create(
        organisation=context.organisation,
        actor=user,
        event_type='calendar_slot.created',
        payload={
            'slot_id': str(slot.id),
            'context_id': str(context.id),
            'venue_id': str(slot.venue_id),
            'date': str(slot.date),
        },
    )
    return slot


def update_calendar_slot(slot, user, data):
    require_programming_calendar_authority(user)
    for key, value in data.items():
        setattr(slot, key, value)
    _validate_calendar_conflicts(
        slot.organisation,
        user,
        context=slot.operating_context,
        venue=slot.venue,
        date_value=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time,
        setup_buffer_minutes=slot.setup_buffer_minutes,
        strike_buffer_minutes=slot.strike_buffer_minutes,
        is_confirmed=slot.is_confirmed,
        is_blocking_slot=slot.slot_type in BLOCKING_SLOT_TYPES,
        source_slot=slot,
        expected_audience=slot.expected_audience,
    )
    slot.save()
    return slot


def create_calendar_issue(organisation, user, data):
    from .models import CalendarIssue

    issue = CalendarIssue.objects.create(
        organisation=organisation,
        raised_by=user,
        **data,
    )
    AuditEvent.objects.create(
        organisation=organisation,
        actor=user,
        event_type='calendar.issue_raised',
        target_type='CalendarIssue',
        target_id=issue.id,
        payload={
            'issue_id': str(issue.id),
            'title': issue.title,
            'severity': issue.severity,
            'context_id': str(issue.operating_context_id) if issue.operating_context_id else None,
            'venue_hold_id': str(issue.venue_hold_id) if issue.venue_hold_id else None,
            'calendar_slot_id': str(issue.calendar_slot_id) if issue.calendar_slot_id else None,
        },
    )
    return issue


def change_calendar_issue_status(issue, user, status, note=''):
    from django.utils import timezone
    from .models import CalendarIssueStatus

    if issue.status in {CalendarIssueStatus.RESOLVED, CalendarIssueStatus.CANCELLED}:
        raise ValidationError({'detail': f"Calendar issue is already '{issue.status}'."})
    old_status = issue.status
    issue.status = status
    update_fields = ['status', 'updated_at']
    if status == CalendarIssueStatus.RESOLVED:
        if not note.strip():
            raise ValidationError({'note': 'A resolution note is required.'})
        issue.resolved_by = user
        issue.resolved_at = timezone.now()
        issue.resolution_note = note
        update_fields.extend(['resolved_by', 'resolved_at', 'resolution_note'])
    issue.save(update_fields=update_fields)
    AuditEvent.objects.create(
        organisation=issue.organisation,
        actor=user,
        event_type=f'calendar.issue_{status}',
        target_type='CalendarIssue',
        target_id=issue.id,
        payload={
            'issue_id': str(issue.id),
            'old_status': old_status,
            'new_status': issue.status,
            'note': note,
        },
    )
    return issue
