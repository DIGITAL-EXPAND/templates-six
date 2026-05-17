import datetime
import pytest
from apps.audit.models import AuditEvent
from apps.youth.models import (
    YouthProject, Activity, Session, LearnerGroup, FacilitatorAssignment,
    ConsentRecord, AttendanceRecord, Assessment, ShowcaseOutput,
)


# ── Model tests ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestYouthModels:
    def test_youth_project_creation(self, org_a, youth_context_a):
        p = YouthProject.objects.create(
            organisation=org_a, operating_context=youth_context_a,
            target_learners=100, target_schools=10, status='planning',
        )
        assert p.status == 'planning'
        assert p.target_learners == 100

    def test_activity_linked_to_project(self, org_a, youth_project_a):
        a = Activity.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            name='Dance Class', activity_type='class_session', recurrence='weekly',
        )
        assert a.youth_project == youth_project_a

    def test_session_linked_to_activity(self, org_a, activity_a):
        s = Session.objects.create(
            organisation=org_a, activity=activity_a,
            session_date=datetime.date(2026, 7, 1),
        )
        assert s.activity == activity_a
        assert s.attendance_captured is False

    def test_learner_group_creation(self, org_a, youth_project_a):
        g = LearnerGroup.objects.create(
            organisation=org_a, youth_project=youth_project_a, name='Brass Section',
        )
        assert g.name == 'Brass Section'

    def test_facilitator_assignment_unique_together(self, org_a, youth_project_a, activity_a, user_a):
        FacilitatorAssignment.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            activity=activity_a, facilitator=user_a, role='Lead',
        )
        with pytest.raises(Exception):
            FacilitatorAssignment.objects.create(
                organisation=org_a, youth_project=youth_project_a,
                activity=activity_a, facilitator=user_a, role='Assistant',
            )

    def test_consent_record_unique_together(self, org_a, youth_project_a):
        ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-001',
        )
        with pytest.raises(Exception):
            ConsentRecord.objects.create(
                organisation=org_a, youth_project=youth_project_a,
                learner_identifier='LRN-001',
            )

    def test_attendance_record_unique_together(self, org_a, session_a):
        AttendanceRecord.objects.create(
            organisation=org_a, session=session_a,
            learner_identifier='LRN-001', present=True,
        )
        with pytest.raises(Exception):
            AttendanceRecord.objects.create(
                organisation=org_a, session=session_a,
                learner_identifier='LRN-001', present=False,
            )

    def test_assessment_creation(self, org_a, youth_project_a, user_a):
        a = Assessment.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-001', assessment_type='formative',
            score='B+', assessor=user_a, assessment_date=datetime.date(2026, 6, 15),
        )
        assert a.assessment_type == 'formative'
        assert a.score == 'B+'

    def test_showcase_output_with_optional_context(self, org_a, youth_project_a, context_a):
        s = ShowcaseOutput.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            output_context=context_a, title='Annual Concert',
            output_type='concert',
        )
        assert s.output_context == context_a


# ── Service tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateYouthProjectService:
    def test_youth_project_context_type_succeeds(self, org_a, youth_context_a, user_a):
        from apps.youth.services import create_youth_project
        p = create_youth_project(youth_context_a, user_a, {'target_learners': 10})
        assert p.operating_context == youth_context_a

    def test_festival_context_type_succeeds(self, org_a, site_a, user_a):
        from apps.contexts.models import OperatingContext
        from apps.youth.services import create_youth_project
        ctx = OperatingContext.objects.create(
            organisation=org_a, title='Festival', context_type='festival',
            site=site_a, owner=user_a,
        )
        p = create_youth_project(ctx, user_a, {})
        assert p.operating_context == ctx

    def test_production_context_type_raises_400(self, context_a, user_a):
        from apps.youth.services import create_youth_project
        from rest_framework.exceptions import ValidationError
        with pytest.raises(ValidationError):
            create_youth_project(context_a, user_a, {})

    def test_create_emits_audit(self, youth_context_a, user_a):
        from apps.youth.services import create_youth_project
        create_youth_project(youth_context_a, user_a, {})
        assert AuditEvent.objects.filter(event_type='YOUTH_PROJECT_CREATED').exists()


@pytest.mark.django_db
class TestCaptureSessionAttendanceService:
    def test_creates_records_for_all_learners(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        data = [
            {'learner_identifier': 'LRN-001', 'present': True},
            {'learner_identifier': 'LRN-002', 'present': False},
            {'learner_identifier': 'LRN-003', 'present': True},
        ]
        records = capture_session_attendance(session_a, user_a, data)
        assert len(records) == 3
        assert AttendanceRecord.objects.filter(session=session_a).count() == 3

    def test_sets_attendance_captured_and_completed(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        capture_session_attendance(session_a, user_a, [
            {'learner_identifier': 'LRN-001', 'present': True},
        ])
        session_a.refresh_from_db()
        assert session_a.attendance_captured is True
        assert session_a.status == 'completed'

    def test_raises_400_for_completed_session(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        from rest_framework.exceptions import ValidationError
        session_a.status = 'completed'
        session_a.save()
        with pytest.raises(ValidationError):
            capture_session_attendance(session_a, user_a, [])

    def test_raises_400_for_cancelled_session(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        from rest_framework.exceptions import ValidationError
        session_a.status = 'cancelled'
        session_a.save()
        with pytest.raises(ValidationError):
            capture_session_attendance(session_a, user_a, [])

    def test_upsert_updates_existing_record(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        capture_session_attendance(session_a, user_a, [
            {'learner_identifier': 'LRN-001', 'present': True},
        ])
        session_a.status = 'scheduled'
        session_a.save()
        capture_session_attendance(session_a, user_a, [
            {'learner_identifier': 'LRN-001', 'present': False, 'notes': 'Late'},
        ])
        assert AttendanceRecord.objects.filter(session=session_a).count() == 1
        rec = AttendanceRecord.objects.get(session=session_a, learner_identifier='LRN-001')
        assert rec.present is False
        assert rec.notes == 'Late'

    def test_emits_audit(self, org_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance
        capture_session_attendance(session_a, user_a, [
            {'learner_identifier': 'LRN-001', 'present': True},
        ])
        assert AuditEvent.objects.filter(event_type='ATTENDANCE_CAPTURED').exists()


@pytest.mark.django_db
class TestGetProjectStatsService:
    def test_returns_correct_counts(self, org_a, youth_project_a, activity_a, session_a, user_a):
        from apps.youth.services import capture_session_attendance, get_project_stats

        ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-001', guardian_consent_received=True,
        )
        ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-002', guardian_consent_received=False,
        )
        capture_session_attendance(session_a, user_a, [
            {'learner_identifier': 'LRN-001', 'present': True},
            {'learner_identifier': 'LRN-002', 'present': False},
        ])
        ShowcaseOutput.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            title='Concert', output_type='concert',
        )

        stats = get_project_stats(youth_project_a)
        assert stats['activity_count'] == 1
        assert stats['total_sessions'] == 1
        assert stats['completed_sessions'] == 1
        assert stats['total_consent_records'] == 2
        assert stats['consented_learners'] == 1
        assert stats['consent_rate'] == 50.0
        assert stats['unique_learners_attended'] == 2
        assert stats['avg_attendance_rate'] == 50.0
        assert stats['showcase_output_count'] == 1

    def test_empty_project_returns_zeros(self, youth_project_a):
        from apps.youth.services import get_project_stats
        stats = get_project_stats(youth_project_a)
        assert stats['activity_count'] == 0
        assert stats['consent_rate'] == 0.0
        assert stats['avg_attendance_rate'] == 0.0


# ── YouthProject CRUD ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestYouthProjectCRUD:
    def test_list(self, client_a, youth_project_a):
        r = client_a.get('/api/v1/youth/projects/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, youth_context_a):
        r = client_a.post('/api/v1/youth/projects/', {
            'operating_context': str(youth_context_a.id),
            'target_learners': 40,
        }, format='json')
        assert r.status_code == 201
        assert YouthProject.objects.filter(organisation=org_a).exists()

    def test_create_emits_audit(self, client_a, youth_context_a):
        client_a.post('/api/v1/youth/projects/', {
            'operating_context': str(youth_context_a.id),
        }, format='json')
        assert AuditEvent.objects.filter(event_type='YOUTH_PROJECT_CREATED').exists()

    def test_create_with_production_context_returns_400(self, client_a, context_a):
        r = client_a.post('/api/v1/youth/projects/', {
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_unique_enforcement(self, client_a, youth_project_a, youth_context_a):
        r = client_a.post('/api/v1/youth/projects/', {
            'operating_context': str(youth_context_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_retrieve(self, client_a, youth_project_a):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_a.id}/')
        assert r.status_code == 200

    def test_partial_update(self, client_a, youth_project_a):
        r = client_a.patch(
            f'/api/v1/youth/projects/{youth_project_a.id}/',
            {'target_learners': 35}, format='json',
        )
        assert r.status_code == 200
        youth_project_a.refresh_from_db()
        assert youth_project_a.target_learners == 35

    def test_direct_status_patch_rejected(self, client_a, youth_project_a):
        r = client_a.patch(
            f'/api/v1/youth/projects/{youth_project_a.id}/',
            {'status': 'recruiting'}, format='json',
        )
        assert r.status_code == 400

    def test_activate_action_sets_status(self, client_a, youth_project_a):
        r = client_a.post(f'/api/v1/youth/projects/{youth_project_a.id}/activate/')
        assert r.status_code == 200
        youth_project_a.refresh_from_db()
        assert youth_project_a.status == 'active'

    def test_cannot_reach_other_org(self, client_a, youth_project_b):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_b.id}/')
        assert r.status_code == 404

    def test_cross_org_context_returns_400(self, client_a, youth_context_b):
        r = client_a.post('/api/v1/youth/projects/', {
            'operating_context': str(youth_context_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        r = APIClient().get('/api/v1/youth/projects/')
        assert r.status_code == 401


# ── Stats action ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestStatsAction:
    def test_stats_returns_aggregated_data(self, client_a, youth_project_a):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_a.id}/stats/')
        assert r.status_code == 200
        assert 'activity_count' in r.data
        assert 'consent_rate' in r.data
        assert 'avg_attendance_rate' in r.data
        assert 'showcase_output_count' in r.data

    def test_stats_other_org_returns_404(self, client_a, youth_project_b):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_b.id}/stats/')
        assert r.status_code == 404


# ── Activity CRUD ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestActivityCRUD:
    def test_list(self, client_a, activity_a):
        r = client_a.get('/api/v1/youth/activities/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, youth_project_a):
        r = client_a.post('/api/v1/youth/activities/', {
            'youth_project': str(youth_project_a.id),
            'name': 'Acting Workshop',
            'activity_type': 'workshop',
            'recurrence': 'weekly',
        }, format='json')
        assert r.status_code == 201
        assert Activity.objects.filter(name='Acting Workshop', organisation=org_a).exists()

    def test_cross_org_youth_project_returns_400(self, client_a, youth_project_b):
        r = client_a.post('/api/v1/youth/activities/', {
            'youth_project': str(youth_project_b.id),
            'name': 'Cross-org Activity',
            'activity_type': 'workshop',
            'recurrence': 'once',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, activity_b):
        r = client_a.get(f'/api/v1/youth/activities/{activity_b.id}/')
        assert r.status_code == 404


# ── Session CRUD & capture-attendance ────────────────────────────────────────

@pytest.mark.django_db
class TestSessionCRUD:
    def test_list(self, client_a, session_a):
        r = client_a.get('/api/v1/youth/sessions/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, activity_a):
        r = client_a.post('/api/v1/youth/sessions/', {
            'activity': str(activity_a.id),
            'session_date': '2026-07-15',
        }, format='json')
        assert r.status_code == 201

    def test_cannot_reach_other_org(self, client_a, session_b):
        r = client_a.get(f'/api/v1/youth/sessions/{session_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestCaptureAttendanceAction:
    def test_capture_attendance_succeeds(self, client_a, session_a):
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/capture-attendance/',
            {'attendance': [
                {'learner_identifier': 'LRN-001', 'present': True},
                {'learner_identifier': 'LRN-002', 'present': False, 'notes': 'Sick'},
            ]}, format='json',
        )
        assert r.status_code == 200
        assert r.data['records_captured'] == 2
        assert r.data['attendance_captured'] is True

    def test_capture_sets_session_completed(self, client_a, session_a):
        client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/capture-attendance/',
            {'attendance': [{'learner_identifier': 'LRN-001', 'present': True}]},
            format='json',
        )
        session_a.refresh_from_db()
        assert session_a.status == 'completed'
        assert session_a.attendance_captured is True

    def test_capture_emits_audit(self, client_a, session_a):
        client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/capture-attendance/',
            {'attendance': [{'learner_identifier': 'LRN-001', 'present': True}]},
            format='json',
        )
        assert AuditEvent.objects.filter(event_type='ATTENDANCE_CAPTURED').exists()

    def test_capture_on_completed_session_returns_400(self, client_a, org_a, session_a):
        session_a.status = 'completed'
        session_a.save()
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/capture-attendance/',
            {'attendance': []}, format='json',
        )
        assert r.status_code == 400

    def test_capture_other_org_session_returns_404(self, client_a, session_b):
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_b.id}/capture-attendance/',
            {'attendance': []}, format='json',
        )
        assert r.status_code == 404

    def test_complete_without_attendance_returns_400(self, client_a, session_a):
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/complete/',
            {'comment': 'Trying to close manually'}, format='json',
        )
        assert r.status_code == 400

    def test_complete_after_attendance_succeeds(self, client_a, session_a):
        client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/capture-attendance/',
            {'attendance': [{'learner_identifier': 'LRN-001', 'present': True}]},
            format='json',
        )
        session_a.status = 'in_progress'
        session_a.save(update_fields=['status'])
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_a.id}/complete/',
            {'comment': 'Attendance confirmed'}, format='json',
        )
        assert r.status_code == 200
        assert r.data['status'] == 'completed'


# ── LearnerGroup CRUD ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLearnerGroupCRUD:
    def test_list(self, client_a, learner_group_a):
        r = client_a.get('/api/v1/youth/learner-groups/')
        assert r.status_code == 200
        assert r.data['count'] == 1

    def test_create(self, client_a, org_a, youth_project_a):
        r = client_a.post('/api/v1/youth/learner-groups/', {
            'youth_project': str(youth_project_a.id),
            'name': 'Wind Section',
        }, format='json')
        assert r.status_code == 201
        assert LearnerGroup.objects.filter(name='Wind Section', organisation=org_a).exists()

    def test_cross_org_project_returns_400(self, client_a, youth_project_b):
        r = client_a.post('/api/v1/youth/learner-groups/', {
            'youth_project': str(youth_project_b.id),
            'name': 'Cross-org group',
        }, format='json')
        assert r.status_code == 400

    def test_cannot_reach_other_org(self, client_a, learner_group_b):
        r = client_a.get(f'/api/v1/youth/learner-groups/{learner_group_b.id}/')
        assert r.status_code == 404


# ── FacilitatorAssignment CRUD ────────────────────────────────────────────────

@pytest.mark.django_db
class TestFacilitatorAssignmentCRUD:
    def test_create(self, client_a, org_a, youth_project_a, activity_a, user_a):
        r = client_a.post('/api/v1/youth/facilitators/', {
            'youth_project': str(youth_project_a.id),
            'activity': str(activity_a.id),
            'facilitator': str(user_a.id),
            'role': 'Lead Facilitator',
        }, format='json')
        assert r.status_code == 201

    def test_duplicate_assignment_returns_400(self, client_a, youth_project_a, activity_a, user_a):
        client_a.post('/api/v1/youth/facilitators/', {
            'youth_project': str(youth_project_a.id),
            'activity': str(activity_a.id),
            'facilitator': str(user_a.id),
            'role': 'Lead',
        }, format='json')
        r = client_a.post('/api/v1/youth/facilitators/', {
            'youth_project': str(youth_project_a.id),
            'activity': str(activity_a.id),
            'facilitator': str(user_a.id),
            'role': 'Assistant',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_facilitator_returns_400(self, client_a, youth_project_a, activity_a, user_b):
        r = client_a.post('/api/v1/youth/facilitators/', {
            'youth_project': str(youth_project_a.id),
            'activity': str(activity_a.id),
            'facilitator': str(user_b.id),
            'role': 'Lead',
        }, format='json')
        assert r.status_code == 400


# ── ConsentRecord CRUD ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestConsentRecordCRUD:
    def test_create(self, client_a, org_a, youth_project_a):
        r = client_a.post('/api/v1/youth/consent/', {
            'youth_project': str(youth_project_a.id),
            'learner_identifier': 'LRN-010',
        }, format='json')
        assert r.status_code == 201
        assert ConsentRecord.objects.filter(
            organisation=org_a, learner_identifier='LRN-010',
        ).exists()

    def test_direct_consent_patch_rejected(self, client_a, org_a, youth_project_a):
        consent = ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a, learner_identifier='LRN-011',
        )
        r = client_a.patch(
            f'/api/v1/youth/consent/{consent.id}/',
            {'guardian_consent_received': True}, format='json',
        )
        assert r.status_code == 400

    def test_receive_consent_action_sets_flag(self, client_a, org_a, youth_project_a):
        consent = ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a, learner_identifier='LRN-012',
        )
        r = client_a.post(f'/api/v1/youth/consent/{consent.id}/receive-consent/')
        assert r.status_code == 200
        consent.refresh_from_db()
        assert consent.guardian_consent_received is True

    def test_duplicate_learner_returns_400(self, client_a, youth_project_a):
        client_a.post('/api/v1/youth/consent/', {
            'youth_project': str(youth_project_a.id),
            'learner_identifier': 'LRN-DUP',
        }, format='json')
        r = client_a.post('/api/v1/youth/consent/', {
            'youth_project': str(youth_project_a.id),
            'learner_identifier': 'LRN-DUP',
        }, format='json')
        assert r.status_code == 400

    def test_cross_org_project_returns_400(self, client_a, youth_project_b):
        r = client_a.post('/api/v1/youth/consent/', {
            'youth_project': str(youth_project_b.id),
            'learner_identifier': 'LRN-CROSS',
        }, format='json')
        assert r.status_code == 400

    def test_filter_by_guardian_consent(self, client_a, org_a, youth_project_a):
        ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-A', guardian_consent_received=True,
        )
        ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-B', guardian_consent_received=False,
        )
        r = client_a.get('/api/v1/youth/consent/?guardian_consent_received=true')
        assert r.data['count'] == 1


# ── AttendanceRecord CRUD ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAttendanceRecordCRUD:
    def test_create(self, client_a, org_a, session_a):
        r = client_a.post('/api/v1/youth/attendance/', {
            'session': str(session_a.id),
            'learner_identifier': 'LRN-ATT',
        }, format='json')
        assert r.status_code == 201

    def test_direct_present_create_rejected(self, client_a, session_a):
        r = client_a.post('/api/v1/youth/attendance/', {
            'session': str(session_a.id),
            'learner_identifier': 'LRN-ATT-2',
            'present': True,
        }, format='json')
        assert r.status_code == 400

    def test_filter_by_present(self, client_a, org_a, session_a):
        AttendanceRecord.objects.create(
            organisation=org_a, session=session_a,
            learner_identifier='LRN-P', present=True,
        )
        AttendanceRecord.objects.create(
            organisation=org_a, session=session_a,
            learner_identifier='LRN-A', present=False,
        )
        r = client_a.get('/api/v1/youth/attendance/?present=true')
        assert r.data['count'] == 1

    def test_cross_org_session_returns_400(self, client_a, session_b):
        r = client_a.post('/api/v1/youth/attendance/', {
            'session': str(session_b.id),
            'learner_identifier': 'LRN-CROSS',
            'present': True,
        }, format='json')
        assert r.status_code == 400


# ── Assessment CRUD ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAssessmentCRUD:
    def test_create(self, client_a, org_a, youth_project_a, user_a):
        r = client_a.post('/api/v1/youth/assessments/', {
            'youth_project': str(youth_project_a.id),
            'learner_identifier': 'LRN-001',
            'assessment_type': 'formative',
            'score': '78%',
            'assessor': str(user_a.id),
            'assessment_date': '2026-06-20',
        }, format='json')
        assert r.status_code == 201
        assert Assessment.objects.filter(organisation=org_a, learner_identifier='LRN-001').exists()

    def test_filter_by_learner_identifier(self, client_a, org_a, youth_project_a, user_a):
        Assessment.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-001', assessment_type='formative',
            assessor=user_a, assessment_date=datetime.date(2026, 6, 1),
        )
        Assessment.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-002', assessment_type='summative',
            assessor=user_a, assessment_date=datetime.date(2026, 6, 1),
        )
        r = client_a.get('/api/v1/youth/assessments/?learner_identifier=LRN-001')
        assert r.data['count'] == 1


# ── ShowcaseOutput CRUD & showcase link test ──────────────────────────────────

@pytest.mark.django_db
class TestShowcaseOutputCRUD:
    def test_create_with_output_context(self, client_a, org_a, youth_project_a, context_a):
        r = client_a.post('/api/v1/youth/showcases/', {
            'youth_project': str(youth_project_a.id),
            'output_context': str(context_a.id),
            'title': 'Soweto Orchestra Annual Concert',
            'output_type': 'concert',
        }, format='json')
        assert r.status_code == 201
        showcase = ShowcaseOutput.objects.get(title='Soweto Orchestra Annual Concert')
        assert showcase.output_context == context_a

    def test_create_without_output_context(self, client_a, org_a, youth_project_a):
        r = client_a.post('/api/v1/youth/showcases/', {
            'youth_project': str(youth_project_a.id),
            'title': 'Exhibition',
            'output_type': 'exhibition',
        }, format='json')
        assert r.status_code == 201

    def test_showcase_links_youth_project_to_production_context(
        self, client_a, org_a, youth_project_a, site_a, user_a,
    ):
        from apps.contexts.models import OperatingContext
        production_ctx = OperatingContext.objects.create(
            organisation=org_a, title='Annual Concert Production',
            context_type='production', site=site_a, owner=user_a,
        )
        r = client_a.post('/api/v1/youth/showcases/', {
            'youth_project': str(youth_project_a.id),
            'output_context': str(production_ctx.id),
            'title': 'Linked Concert',
            'output_type': 'concert',
        }, format='json')
        assert r.status_code == 201
        showcase = ShowcaseOutput.objects.get(title='Linked Concert')
        assert showcase.youth_project == youth_project_a
        assert showcase.output_context == production_ctx
        # Both contexts accessible
        assert OperatingContext.objects.filter(pk=youth_project_a.operating_context_id).exists()
        assert OperatingContext.objects.filter(pk=production_ctx.pk).exists()

    def test_filter_by_output_type(self, client_a, org_a, youth_project_a):
        ShowcaseOutput.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            title='Concert', output_type='concert',
        )
        ShowcaseOutput.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            title='Exhibition', output_type='exhibition',
        )
        r = client_a.get('/api/v1/youth/showcases/?output_type=concert')
        assert r.data['count'] == 1

    def test_cannot_reach_other_org(self, client_a, org_b, youth_project_b):
        s = ShowcaseOutput.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            title='B Showcase', output_type='performance',
        )
        r = client_a.get(f'/api/v1/youth/showcases/{s.id}/')
        assert r.status_code == 404
