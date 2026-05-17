import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.audit.models import AuditEvent
from apps.documents.models import EvidenceSubmission
from apps.programming.models import IntakeRequest, CalendarIssue
from apps.contexts.models import OperatingContext
from apps.tasks.models import Task


@pytest.mark.django_db
class TestMasterTheatreJourney:
    def test_intake_to_workspace_evidence_calendar_reports_and_audit(
        self, client_a, org_a, user_a, site_a, venue_a,
    ):
        from apps.structure.models import Department
        from apps.approvals.models import ApprovalRoute, ApprovalStep
        from apps.workflows.models import WorkflowTemplate, WorkflowStepTemplate, WorkflowStepInstance

        programming = Department.objects.create(
            organisation=org_a,
            name='Programming Office',
            code='PROG',
            department_type='programming',
            site=site_a,
        )
        marketing = Department.objects.create(
            organisation=org_a,
            name='Marketing and Communications',
            code='MKT',
            department_type='marketing',
            site=site_a,
        )

        intake_response = client_a.post('/api/v1/programming/intake-requests/', {
            'request_type': 'venue_booking',
            'event_title': 'UAT Gala Night',
            'client_name': 'Cape Client',
            'client_organisation': 'Cape Client Org',
            'contact_email': 'client@example.com',
            'requested_start_date': '2026-09-20',
            'requested_end_date': '2026-09-20',
            'preferred_venue': str(venue_a.id),
            'expected_audience': 300,
            'ticketing_required': True,
            'technical_summary': 'Basic lighting and handheld microphone.',
            'foh_notes': 'VIP arrivals expected.',
            'accessibility_requirements': 'Wheelchair access required.',
        }, format='json')
        assert intake_response.status_code == 201
        intake_id = intake_response.data['id']

        assert client_a.post(
            f'/api/v1/programming/intake-requests/{intake_id}/start-review/',
            {'comment': 'Programming review started.'},
            format='json',
        ).status_code == 200

        approve_response = client_a.post(
            f'/api/v1/programming/intake-requests/{intake_id}/approve/',
            {'comment': 'Approved for controlled UAT delivery.'},
            format='json',
        )
        assert approve_response.status_code == 200

        convert_response = client_a.post(
            f'/api/v1/programming/intake-requests/{intake_id}/convert-to-workspace/',
            {
                'site': str(site_a.id),
                'venue': str(venue_a.id),
                'owner': str(user_a.id),
                'department': str(programming.id),
                'priority': 'high',
                'risk_level': 'medium',
                'budget': '25000.00',
            },
            format='json',
        )
        assert convert_response.status_code == 201
        workspace_id = convert_response.data['workspace_id']
        assert OperatingContext.objects.filter(id=workspace_id, organisation=org_a).exists()
        assert IntakeRequest.objects.get(id=intake_id).status == 'converted'

        hold_response = client_a.post('/api/v1/programming/venue-holds/', {
            'operating_context': workspace_id,
            'venue': str(venue_a.id),
            'hold_date': '2026-09-20',
            'start_time': '17:00:00',
            'end_time': '22:00:00',
            'hold_type': 'provisional',
            'purpose': 'performance',
            'notes': 'Created during master journey test.',
        }, format='json')
        assert hold_response.status_code == 201

        task_response = client_a.post('/api/v1/tasks/', {
            'operating_context': workspace_id,
            'department': str(marketing.id),
            'assigned_to': str(user_a.id),
            'title': 'Upload approved artwork evidence',
            'priority': 'high',
            'evidence_required': True,
        }, format='json')
        assert task_response.status_code == 201
        task_id = task_response.data['id']

        blocked_completion = client_a.post(
            f'/api/v1/tasks/{task_id}/complete/',
            {'has_evidence': True},
            format='json',
        )
        assert blocked_completion.status_code == 422

        upload_response = client_a.post('/api/v1/documents/upload/', {
            'operating_context': workspace_id,
            'title': 'Approved artwork proof',
            'document_type': 'marketing_asset',
            'file': SimpleUploadedFile('artwork-proof.pdf', b'%PDF-1.4 UAT', content_type='application/pdf'),
        }, format='multipart')
        assert upload_response.status_code == 201
        document_id = upload_response.data['id']

        evidence_response = client_a.post('/api/v1/evidence/', {
            'operating_context': workspace_id,
            'task': task_id,
            'document': document_id,
            'submission_note': 'Artwork proof submitted for UAT.',
        }, format='json')
        assert evidence_response.status_code == 201
        evidence_id = evidence_response.data['id']

        accept_response = client_a.post(f'/api/v1/evidence/{evidence_id}/accept/')
        assert accept_response.status_code == 200
        assert EvidenceSubmission.objects.get(id=evidence_id).accepted is True

        complete_response = client_a.post(
            f'/api/v1/tasks/{task_id}/complete/',
            {'has_evidence': True},
            format='json',
        )
        assert complete_response.status_code == 200
        assert Task.objects.get(id=task_id).status == 'done'

        route = ApprovalRoute.objects.create(
            organisation=org_a,
            name='UAT Approval Route',
            context_type='venue_rental',
        )
        step = ApprovalStep.objects.create(
            organisation=org_a,
            route=route,
            step_number=1,
            name='GM Approval',
            approver_department=programming,
        )
        approval_request = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': workspace_id,
            'approval_step': str(step.id),
            'decision_comment': 'Approval requested by UAT journey.',
        }, format='json')
        assert approval_request.status_code == 201
        approval_id = approval_request.data['id']
        approval_decision = client_a.post(
            f'/api/v1/approvals/requests/{approval_id}/approve/',
            {'comment': 'Approved for delivery.', 'evidence': document_id},
            format='json',
        )
        assert approval_decision.status_code == 200

        template = WorkflowTemplate.objects.create(
            organisation=org_a,
            name='UAT Delivery Process',
            context_type='venue_rental',
        )
        WorkflowStepTemplate.objects.create(
            organisation=org_a,
            template=template,
            step_number=1,
            name='Evidence and approval gate',
            owner_department=marketing,
            owner_role_description='Head of Marketing and Communications',
            requires_evidence=True,
            requires_approval=True,
            sla_days=2,
        )
        workflow_response = client_a.post('/api/v1/workflows/instances/', {
            'template': str(template.id),
            'operating_context': workspace_id,
        }, format='json')
        assert workflow_response.status_code == 201
        process_step = WorkflowStepInstance.objects.get(
            workflow_instance_id=workflow_response.data['id'],
            step_number=1,
        )
        advance_response = client_a.post(
            f'/api/v1/workflows/steps/{process_step.id}/advance/',
            {
                'notes': 'Evidence and approval confirmed.',
                'evidence_document': document_id,
                'approval_request': approval_id,
            },
            format='json',
        )
        assert advance_response.status_code == 200

        issue_response = client_a.post('/api/v1/programming/calendar-issues/', {
            'title': 'UAT load-in clash',
            'description': 'Potential clash detected during test.',
            'operating_context': workspace_id,
            'department': str(marketing.id),
            'severity': 'high',
            'due_date': '2026-09-10',
        }, format='json')
        assert issue_response.status_code == 201
        issue_id = issue_response.data['id']
        assert client_a.post(
            f'/api/v1/programming/calendar-issues/{issue_id}/progress/',
            {'note': 'Marketing reviewing clash.'},
            format='json',
        ).status_code == 200
        assert client_a.post(
            f'/api/v1/programming/calendar-issues/{issue_id}/resolve/',
            {'note': 'Resolved by adjusting load-in call time.'},
            format='json',
        ).status_code == 200
        assert CalendarIssue.objects.get(id=issue_id).status == 'resolved'

        action_response = client_a.post('/api/v1/governance/executive-actions/', {
            'action_type': 'request_change',
            'title': 'Correct campaign proof',
            'reason': 'Artwork must match approved institutional positioning.',
            'instruction': 'Confirm approved title and funder logo.',
            'operating_context': workspace_id,
            'department': str(marketing.id),
            'assigned_to': str(user_a.id),
            'target_type': 'Document',
            'target_id': document_id,
            'due_date': '2026-09-05',
        }, format='json')
        assert action_response.status_code == 201
        action_id = action_response.data['id']
        assert client_a.post(
            f'/api/v1/governance/executive-actions/{action_id}/acknowledge/',
            {'comment': 'Marketing has accepted the instruction.'},
            format='json',
        ).status_code == 200
        assert client_a.post(
            f'/api/v1/governance/executive-actions/{action_id}/complete/',
            {'comment': 'Campaign proof corrected.'},
            format='json',
        ).status_code == 200

        report_response = client_a.get(f'/api/v1/reports/context-readiness/{workspace_id}/')
        assert report_response.status_code == 200
        assert report_response.data['tasks']['done'] == 1
        assert report_response.data['documents_count'] == 1

        audit_response = client_a.get(f'/api/v1/reports/context-audit/{workspace_id}/')
        assert audit_response.status_code == 200
        assert audit_response.data['count'] >= 1
        event_types = set(AuditEvent.objects.filter(organisation=org_a).values_list('event_type', flat=True))
        assert {
            'intake.request_submitted',
            'intake.converted_to_workspace',
            'document.file_uploaded',
            'evidence.submitted',
            'evidence.accepted',
            'task.completed',
            'calendar.issue_raised',
            'calendar.issue_resolved',
            'executive.action_created',
            'executive.action_completed',
            'workflow.step_completed',
        }.issubset(event_types)

        assert client_a.get('/api/v1/reports/executive-summary/').status_code == 200
        assert client_a.get('/api/v1/reports/board-summary/').status_code == 200
        assert client_a.get('/api/v1/reports/calendar-issues/').status_code == 200
        assert client_a.get('/api/v1/reports/evidence-gaps/').status_code == 200
