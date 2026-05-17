import pytest
from apps.audit.models import AuditEvent
from apps.accounts.models import User
from apps.structure.models import Site, Venue, Space, Department, Position


@pytest.mark.django_db
class TestTenantIsolation:
    def test_users_list_excludes_other_org(self, client_a, user_b):
        response = client_a.get('/api/v1/users/')
        assert response.status_code == 200
        ids = [u['id'] for u in response.data['results']]
        assert str(user_b.id) not in ids

    def test_users_list_includes_own_org(self, client_a, user_a):
        response = client_a.get('/api/v1/users/')
        assert response.status_code == 200
        ids = [u['id'] for u in response.data['results']]
        assert str(user_a.id) in ids

    def test_organisations_list_excludes_other_org(self, client_a, org_b):
        response = client_a.get('/api/v1/organisations/')
        assert response.status_code == 200
        ids = [o['id'] for o in response.data['results']]
        assert str(org_b.id) not in ids

    def test_organisations_list_includes_own_org(self, client_a, org_a):
        response = client_a.get('/api/v1/organisations/')
        assert response.status_code == 200
        ids = [o['id'] for o in response.data['results']]
        assert str(org_a.id) in ids

    def test_audit_excludes_other_org_events(self, client_a, org_b):
        AuditEvent.objects.create(organisation=org_b, event_type='test.event')
        response = client_a.get('/api/v1/audit/')
        assert response.status_code == 200
        assert response.data['count'] == 0

    def test_audit_includes_own_org_events(self, client_a, org_a):
        AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        response = client_a.get('/api/v1/audit/')
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_unauthenticated_users_are_rejected(self):
        from rest_framework.test import APIClient
        anon = APIClient()
        for url in ['/api/v1/users/', '/api/v1/organisations/', '/api/v1/audit/']:
            response = anon.get(url)
            assert response.status_code == 401, f'Expected 401 for {url}'

    def test_create_user_is_scoped_to_own_org(self, client_a, org_a):
        response = client_a.post('/api/v1/users/', {
            'email': 'new@example.com',
            'password': 'newpass123',
            'user_type': 'staff',
        }, format='json')
        assert response.status_code == 201
        new_user = User.objects.get(email='new@example.com')
        assert new_user.organisation == org_a


@pytest.mark.django_db
class TestStructureTenantIsolation:
    # Sites
    def test_sites_exclude_other_org(self, client_a, site_a, site_b):
        r = client_a.get('/api/v1/sites/')
        ids = [s['id'] for s in r.data['results']]
        assert str(site_a.id) in ids
        assert str(site_b.id) not in ids

    def test_site_retrieve_other_org_returns_404(self, client_a, site_b):
        r = client_a.get(f'/api/v1/sites/{site_b.id}/')
        assert r.status_code == 404

    def test_site_update_other_org_returns_404(self, client_a, site_b):
        r = client_a.patch(f'/api/v1/sites/{site_b.id}/', {'name': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_site_delete_other_org_returns_404(self, client_a, site_b):
        r = client_a.delete(f'/api/v1/sites/{site_b.id}/')
        assert r.status_code == 404

    # Venues
    def test_venues_exclude_other_org(self, client_a, venue_a, venue_b):
        r = client_a.get('/api/v1/venues/')
        ids = [v['id'] for v in r.data['results']]
        assert str(venue_a.id) in ids
        assert str(venue_b.id) not in ids

    def test_venue_retrieve_other_org_returns_404(self, client_a, venue_b):
        r = client_a.get(f'/api/v1/venues/{venue_b.id}/')
        assert r.status_code == 404

    def test_venue_create_with_other_org_site_rejected(self, client_a, site_b):
        r = client_a.post('/api/v1/venues/', {
            'name': 'Cross-tenant Venue', 'site': str(site_b.id),
            'venue_type': 'performance', 'capacity': 100,
        }, format='json')
        assert r.status_code == 400

    # Spaces
    def test_spaces_exclude_other_org(self, client_a, org_a, org_b, venue_a, venue_b):
        Space.objects.create(organisation=org_a, name='Sp-A', venue=venue_a, space_type='stage', capacity=100)
        Space.objects.create(organisation=org_b, name='Sp-B', venue=venue_b, space_type='studio', capacity=50)
        r = client_a.get('/api/v1/spaces/')
        names = [s['name'] for s in r.data['results']]
        assert 'Sp-A' in names
        assert 'Sp-B' not in names

    def test_space_create_with_other_org_venue_rejected(self, client_a, venue_b):
        r = client_a.post('/api/v1/spaces/', {
            'name': 'Cross-tenant Space', 'venue': str(venue_b.id),
            'space_type': 'stage', 'capacity': 100,
        }, format='json')
        assert r.status_code == 400

    # Departments
    def test_departments_exclude_other_org(self, client_a, department_a, department_b):
        r = client_a.get('/api/v1/departments/')
        ids = [d['id'] for d in r.data['results']]
        assert str(department_a.id) in ids
        assert str(department_b.id) not in ids

    def test_department_retrieve_other_org_returns_404(self, client_a, department_b):
        r = client_a.get(f'/api/v1/departments/{department_b.id}/')
        assert r.status_code == 404

    def test_department_create_with_other_org_site_rejected(self, client_a, site_b):
        r = client_a.post('/api/v1/departments/', {
            'name': 'Cross-tenant Dept', 'code': 'CTD',
            'department_type': 'technical', 'site': str(site_b.id),
        }, format='json')
        assert r.status_code == 400

    # Positions
    def test_positions_exclude_other_org(self, client_a, org_a, org_b, department_a, department_b):
        Position.objects.create(organisation=org_a, title='Pos-A', department=department_a, level='officer')
        Position.objects.create(organisation=org_b, title='Pos-B', department=department_b, level='officer')
        r = client_a.get('/api/v1/positions/')
        titles = [p['title'] for p in r.data['results']]
        assert 'Pos-A' in titles
        assert 'Pos-B' not in titles

    def test_position_create_with_other_org_department_rejected(self, client_a, department_b):
        r = client_a.post('/api/v1/positions/', {
            'title': 'Cross-tenant Pos', 'department': str(department_b.id),
            'level': 'officer',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestContextTenantIsolation:
    def test_contexts_exclude_other_org(self, client_a, context_a, context_b):
        r = client_a.get('/api/v1/contexts/')
        ids = [c['id'] for c in r.data['results']]
        assert str(context_a.id) in ids
        assert str(context_b.id) not in ids

    def test_context_retrieve_other_org_returns_404(self, client_a, context_b):
        r = client_a.get(f'/api/v1/contexts/{context_b.id}/')
        assert r.status_code == 404

    def test_context_update_other_org_returns_404(self, client_a, context_b):
        r = client_a.patch(f'/api/v1/contexts/{context_b.id}/', {'title': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_context_delete_other_org_returns_404(self, client_a, context_b):
        r = client_a.delete(f'/api/v1/contexts/{context_b.id}/')
        assert r.status_code == 404

    def test_change_status_other_org_returns_404(self, client_a, context_b):
        r = client_a.post(
            f'/api/v1/contexts/{context_b.id}/change-status/',
            {'status': 'submitted'},
            format='json',
        )
        assert r.status_code == 404

    def test_create_with_other_org_site_rejected(self, client_a, site_b, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_b.id), 'owner': str(user_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_owner_rejected(self, client_a, site_a, user_b):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_a.id), 'owner': str(user_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_venue_rejected(self, client_a, site_a, user_a, venue_b):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Cross-tenant', 'site': str(site_a.id),
            'owner': str(user_a.id), 'venue': str(venue_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_filter_cannot_reveal_other_org_contexts(self, client_a, context_a, context_b):
        r = client_a.get(f'/api/v1/contexts/?search={context_b.title}')
        assert r.status_code == 200
        assert r.data['count'] == 0


@pytest.mark.django_db
class TestTaskTenantIsolation:
    def test_tasks_exclude_other_org(self, client_a, task_a, task_b):
        r = client_a.get('/api/v1/tasks/')
        ids = [t['id'] for t in r.data['results']]
        assert str(task_a.id) in ids
        assert str(task_b.id) not in ids

    def test_task_retrieve_other_org_returns_404(self, client_a, task_b):
        r = client_a.get(f'/api/v1/tasks/{task_b.id}/')
        assert r.status_code == 404

    def test_task_update_other_org_returns_404(self, client_a, task_b):
        r = client_a.patch(f'/api/v1/tasks/{task_b.id}/', {'title': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_task_delete_other_org_returns_404(self, client_a, task_b):
        r = client_a.delete(f'/api/v1/tasks/{task_b.id}/')
        assert r.status_code == 404

    def test_complete_other_org_task_returns_404(self, client_a, task_b):
        r = client_a.post(f'/api/v1/tasks/{task_b.id}/complete/', {}, format='json')
        assert r.status_code == 404

    def test_create_with_other_org_context_rejected(self, client_a, context_b):
        r = client_a.post('/api/v1/tasks/', {
            'operating_context': str(context_b.id),
            'title': 'Cross-tenant task',
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestDocumentTenantIsolation:
    def test_documents_exclude_other_org(self, client_a, document_a, document_b):
        r = client_a.get('/api/v1/documents/')
        ids = [d['id'] for d in r.data['results']]
        assert str(document_a.id) in ids
        assert str(document_b.id) not in ids

    def test_document_retrieve_other_org_returns_404(self, client_a, document_b):
        r = client_a.get(f'/api/v1/documents/{document_b.id}/')
        assert r.status_code == 404

    def test_document_update_other_org_returns_404(self, client_a, document_b):
        r = client_a.patch(f'/api/v1/documents/{document_b.id}/', {'title': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_document_delete_other_org_returns_404(self, client_a, document_b):
        r = client_a.delete(f'/api/v1/documents/{document_b.id}/')
        assert r.status_code == 404

    def test_create_with_other_org_context_rejected(self, client_a, context_b):
        r = client_a.post('/api/v1/documents/', {
            'operating_context': str(context_b.id),
            'title': 'Cross-org doc',
            'document_type': 'brief',
            'file_name': 'x.pdf',
            'file_size': 1024,
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestEvidenceTenantIsolation:
    def _make_submission(self, org, context, task, document, user):
        from apps.documents.models import EvidenceSubmission
        return EvidenceSubmission.objects.create(
            organisation=org, operating_context=context,
            task=task, document=document, submitted_by=user,
        )

    def test_evidence_excludes_other_org(self, client_a, org_a, org_b, context_a, context_b,
                                         task_a, task_b, document_a, document_b, user_a, user_b):
        sub_a = self._make_submission(org_a, context_a, task_a, document_a, user_a)
        sub_b = self._make_submission(org_b, context_b, task_b, document_b, user_b)
        r = client_a.get('/api/v1/evidence/')
        ids = [e['id'] for e in r.data['results']]
        assert str(sub_a.id) in ids
        assert str(sub_b.id) not in ids

    def test_evidence_retrieve_other_org_returns_404(self, client_a, org_b, context_b,
                                                     task_b, document_b, user_b):
        sub_b = self._make_submission(org_b, context_b, task_b, document_b, user_b)
        r = client_a.get(f'/api/v1/evidence/{sub_b.id}/')
        assert r.status_code == 404

    def test_accept_other_org_evidence_returns_404(self, client_a, org_b, context_b,
                                                   task_b, document_b, user_b):
        sub_b = self._make_submission(org_b, context_b, task_b, document_b, user_b)
        r = client_a.post(f'/api/v1/evidence/{sub_b.id}/accept/')
        assert r.status_code == 404

    def test_create_with_other_org_document_rejected(self, client_a, context_a, document_b):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'document': str(document_b.id),
        }, format='json')
        assert r.status_code == 400

    def test_create_with_other_org_task_rejected(self, client_a, context_a, document_a, task_b):
        r = client_a.post('/api/v1/evidence/', {
            'operating_context': str(context_a.id),
            'document': str(document_a.id),
            'task': str(task_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestWorkflowTenantIsolation:
    def _make_template(self, org, name='WF Template'):
        from apps.workflows.models import WorkflowTemplate
        return WorkflowTemplate.objects.create(
            organisation=org, name=name, context_type='production',
        )

    def _make_instance(self, org, template, context, user):
        from apps.workflows.services import instantiate_workflow
        from apps.workflows.models import WorkflowStepTemplate
        WorkflowStepTemplate.objects.create(
            organisation=org, template=template, step_number=1, name='Step 1',
        )
        return instantiate_workflow(context=context, template=template, user=user)

    def test_templates_exclude_other_org(self, client_a, org_a, org_b):
        tpl_a = self._make_template(org_a, 'TplA')
        tpl_b = self._make_template(org_b, 'TplB')
        r = client_a.get('/api/v1/workflows/templates/')
        ids = [t['id'] for t in r.data['results']]
        assert str(tpl_a.id) in ids
        assert str(tpl_b.id) not in ids

    def test_template_retrieve_other_org_returns_404(self, client_a, org_b):
        tpl_b = self._make_template(org_b)
        r = client_a.get(f'/api/v1/workflows/templates/{tpl_b.id}/')
        assert r.status_code == 404

    def test_instances_exclude_other_org(self, client_a, org_a, org_b, context_a, context_b, user_a, user_b):
        tpl_a = self._make_template(org_a, 'TplA')
        tpl_b = self._make_template(org_b, 'TplB')
        inst_a = self._make_instance(org_a, tpl_a, context_a, user_a)
        inst_b = self._make_instance(org_b, tpl_b, context_b, user_b)
        r = client_a.get('/api/v1/workflows/instances/')
        ids = [i['id'] for i in r.data['results']]
        assert str(inst_a.id) in ids
        assert str(inst_b.id) not in ids

    def test_instance_retrieve_other_org_returns_404(self, client_a, org_b, context_b, user_b):
        tpl_b = self._make_template(org_b)
        inst_b = self._make_instance(org_b, tpl_b, context_b, user_b)
        r = client_a.get(f'/api/v1/workflows/instances/{inst_b.id}/')
        assert r.status_code == 404

    def test_step_instances_exclude_other_org(self, client_a, org_a, org_b,
                                              context_a, context_b, user_a, user_b):
        tpl_a = self._make_template(org_a, 'TplA')
        tpl_b = self._make_template(org_b, 'TplB')
        inst_a = self._make_instance(org_a, tpl_a, context_a, user_a)
        inst_b = self._make_instance(org_b, tpl_b, context_b, user_b)
        r = client_a.get('/api/v1/workflows/steps/')
        from apps.workflows.models import WorkflowStepInstance
        ids_a = [str(s.id) for s in WorkflowStepInstance.objects.filter(workflow_instance=inst_a)]
        ids_b = [str(s.id) for s in WorkflowStepInstance.objects.filter(workflow_instance=inst_b)]
        result_ids = [s['id'] for s in r.data['results']]
        assert all(i in result_ids for i in ids_a)
        assert all(i not in result_ids for i in ids_b)

    def test_instantiate_with_other_org_template_rejected(self, client_a, context_a, org_b):
        tpl_b = self._make_template(org_b)
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(tpl_b.id),
            'operating_context': str(context_a.id),
        }, format='json')
        assert r.status_code == 400

    def test_instantiate_with_other_org_context_rejected(self, client_a, org_a, context_b):
        tpl_a = self._make_template(org_a)
        r = client_a.post('/api/v1/workflows/instances/', {
            'template': str(tpl_a.id),
            'operating_context': str(context_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestApprovalTenantIsolation:
    def _make_route(self, org, name='Test Route'):
        from apps.approvals.models import ApprovalRoute
        return ApprovalRoute.objects.create(organisation=org, name=name)

    def _make_step(self, org, route, number=1):
        from apps.approvals.models import ApprovalStep
        return ApprovalStep.objects.create(
            organisation=org, route=route, step_number=number, name=f'Step {number}',
        )

    def _make_request(self, org, context, step, user):
        from apps.approvals.models import ApprovalRequest
        return ApprovalRequest.objects.create(
            organisation=org, operating_context=context,
            approval_step=step, requested_by=user,
        )

    def test_routes_exclude_other_org(self, client_a, org_a, org_b):
        route_a = self._make_route(org_a, 'RouteA')
        route_b = self._make_route(org_b, 'RouteB')
        r = client_a.get('/api/v1/approvals/routes/')
        ids = [x['id'] for x in r.data['results']]
        assert str(route_a.id) in ids
        assert str(route_b.id) not in ids

    def test_route_retrieve_other_org_returns_404(self, client_a, org_b):
        route_b = self._make_route(org_b)
        r = client_a.get(f'/api/v1/approvals/routes/{route_b.id}/')
        assert r.status_code == 404

    def test_requests_exclude_other_org(self, client_a, org_a, org_b,
                                        context_a, context_b, user_a, user_b):
        route_a = self._make_route(org_a, 'RA')
        route_b = self._make_route(org_b, 'RB')
        step_a = self._make_step(org_a, route_a)
        step_b = self._make_step(org_b, route_b)
        req_a = self._make_request(org_a, context_a, step_a, user_a)
        req_b = self._make_request(org_b, context_b, step_b, user_b)
        r = client_a.get('/api/v1/approvals/requests/')
        ids = [x['id'] for x in r.data['results']]
        assert str(req_a.id) in ids
        assert str(req_b.id) not in ids

    def test_request_retrieve_other_org_returns_404(self, client_a, org_b, context_b, user_b):
        route_b = self._make_route(org_b)
        step_b = self._make_step(org_b, route_b)
        req_b = self._make_request(org_b, context_b, step_b, user_b)
        r = client_a.get(f'/api/v1/approvals/requests/{req_b.id}/')
        assert r.status_code == 404

    def test_approve_other_org_request_returns_404(self, client_a, org_b, context_b, user_b):
        route_b = self._make_route(org_b)
        step_b = self._make_step(org_b, route_b)
        req_b = self._make_request(org_b, context_b, step_b, user_b)
        r = client_a.post(f'/api/v1/approvals/requests/{req_b.id}/approve/', {}, format='json')
        assert r.status_code == 404

    def test_create_step_with_other_org_route_rejected(self, client_a, org_b):
        route_b = self._make_route(org_b)
        r = client_a.post('/api/v1/approvals/steps/', {
            'route': str(route_b.id),
            'step_number': 1,
            'name': 'Cross-org Step',
        }, format='json')
        assert r.status_code == 400

    def test_create_request_with_other_org_step_rejected(self, client_a, context_a, org_b):
        route_b = self._make_route(org_b)
        step_b = self._make_step(org_b, route_b)
        r = client_a.post('/api/v1/approvals/requests/', {
            'operating_context': str(context_a.id),
            'approval_step': str(step_b.id),
        }, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestProgrammingTenantIsolation:
    def test_intake_reviews_exclude_other_org(self, client_a, intake_review_a, intake_review_b):
        r = client_a.get('/api/v1/programming/intake-reviews/')
        ids = [x['id'] for x in r.data['results']]
        assert str(intake_review_a.id) in ids
        assert str(intake_review_b.id) not in ids

    def test_intake_review_retrieve_other_org_returns_404(self, client_a, intake_review_b):
        r = client_a.get(f'/api/v1/programming/intake-reviews/{intake_review_b.id}/')
        assert r.status_code == 404

    def test_intake_review_update_other_org_returns_404(self, client_a, intake_review_b):
        r = client_a.patch(
            f'/api/v1/programming/intake-reviews/{intake_review_b.id}/',
            {'status': 'reviewed'}, format='json',
        )
        assert r.status_code == 404

    def test_venue_holds_exclude_other_org(self, client_a, venue_hold_a, venue_hold_b):
        r = client_a.get('/api/v1/programming/venue-holds/')
        ids = [x['id'] for x in r.data['results']]
        assert str(venue_hold_a.id) in ids
        assert str(venue_hold_b.id) not in ids

    def test_venue_hold_retrieve_other_org_returns_404(self, client_a, venue_hold_b):
        r = client_a.get(f'/api/v1/programming/venue-holds/{venue_hold_b.id}/')
        assert r.status_code == 404

    def test_calendar_slots_exclude_other_org(self, client_a, calendar_slot_a, calendar_slot_b):
        r = client_a.get('/api/v1/programming/calendar-slots/')
        ids = [x['id'] for x in r.data['results']]
        assert str(calendar_slot_a.id) in ids
        assert str(calendar_slot_b.id) not in ids

    def test_calendar_slot_retrieve_other_org_returns_404(self, client_a, calendar_slot_b):
        r = client_a.get(f'/api/v1/programming/calendar-slots/{calendar_slot_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestMarketingTenantIsolation:
    def test_campaigns_exclude_other_org(self, client_a, campaign_a, campaign_b):
        r = client_a.get('/api/v1/marketing/campaigns/')
        ids = [x['id'] for x in r.data['results']]
        assert str(campaign_a.id) in ids
        assert str(campaign_b.id) not in ids

    def test_campaign_retrieve_other_org_returns_404(self, client_a, campaign_b):
        r = client_a.get(f'/api/v1/marketing/campaigns/{campaign_b.id}/')
        assert r.status_code == 404

    def test_campaign_update_other_org_returns_404(self, client_a, campaign_b):
        r = client_a.patch(
            f'/api/v1/marketing/campaigns/{campaign_b.id}/',
            {'status': 'active'}, format='json',
        )
        assert r.status_code == 404

    def test_deliverables_exclude_other_org(self, client_a, deliverable_a, deliverable_b):
        r = client_a.get('/api/v1/marketing/deliverables/')
        ids = [x['id'] for x in r.data['results']]
        assert str(deliverable_a.id) in ids
        assert str(deliverable_b.id) not in ids

    def test_deliverable_retrieve_other_org_returns_404(self, client_a, deliverable_b):
        r = client_a.get(f'/api/v1/marketing/deliverables/{deliverable_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestTechnicalTenantIsolation:
    def test_riders_exclude_other_org(self, client_a, rider_a, rider_b):
        r = client_a.get('/api/v1/technical/riders/')
        ids = [x['id'] for x in r.data['results']]
        assert str(rider_a.id) in ids
        assert str(rider_b.id) not in ids

    def test_rider_retrieve_other_org_returns_404(self, client_a, rider_b):
        r = client_a.get(f'/api/v1/technical/riders/{rider_b.id}/')
        assert r.status_code == 404

    def test_rider_update_other_org_returns_404(self, client_a, rider_b):
        r = client_a.patch(
            f'/api/v1/technical/riders/{rider_b.id}/',
            {'lighting': 'Hacked'}, format='json',
        )
        assert r.status_code == 404

    def test_approve_other_org_rider_returns_404(self, client_a, rider_b):
        r = client_a.post(f'/api/v1/technical/riders/{rider_b.id}/approve/', {}, format='json')
        assert r.status_code == 404


@pytest.mark.django_db
class TestOperationsTenantIsolation:
    def test_foh_plans_exclude_other_org(self, client_a, foh_plan_a, foh_plan_b):
        r = client_a.get('/api/v1/operations/foh-plans/')
        ids = [x['id'] for x in r.data['results']]
        assert str(foh_plan_a.id) in ids
        assert str(foh_plan_b.id) not in ids

    def test_foh_plan_retrieve_other_org_returns_404(self, client_a, foh_plan_b):
        r = client_a.get(f'/api/v1/operations/foh-plans/{foh_plan_b.id}/')
        assert r.status_code == 404

    def test_foh_plan_update_other_org_returns_404(self, client_a, foh_plan_b):
        r = client_a.patch(
            f'/api/v1/operations/foh-plans/{foh_plan_b.id}/',
            {'status': 'confirmed'}, format='json',
        )
        assert r.status_code == 404

    def test_incidents_exclude_other_org(self, client_a, org_a, org_b,
                                         context_a, context_b, user_a, user_b):
        from apps.operations.models import Incident
        inc_a = Incident.objects.create(
            organisation=org_a, operating_context=context_a,
            incident_type='other', occurred_at='2026-05-07T20:00:00Z',
            description='A', severity='low', reported_by=user_a,
        )
        inc_b = Incident.objects.create(
            organisation=org_b, operating_context=context_b,
            incident_type='other', occurred_at='2026-05-07T20:00:00Z',
            description='B', severity='low', reported_by=user_b,
        )
        r = client_a.get('/api/v1/operations/incidents/')
        ids = [x['id'] for x in r.data['results']]
        assert str(inc_a.id) in ids
        assert str(inc_b.id) not in ids

    def test_incident_retrieve_other_org_returns_404(self, client_a, org_b, context_b, user_b):
        from apps.operations.models import Incident
        inc_b = Incident.objects.create(
            organisation=org_b, operating_context=context_b,
            incident_type='other', occurred_at='2026-05-07T20:00:00Z',
            description='B', severity='low', reported_by=user_b,
        )
        r = client_a.get(f'/api/v1/operations/incidents/{inc_b.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestContractsTenantIsolation:
    def test_templates_exclude_other_org(self, client_a, contract_template_a, contract_template_b):
        r = client_a.get('/api/v1/contracts/templates/')
        ids = [x['id'] for x in r.data['results']]
        assert str(contract_template_a.id) in ids
        assert str(contract_template_b.id) not in ids

    def test_template_retrieve_other_org_returns_404(self, client_a, contract_template_b):
        r = client_a.get(f'/api/v1/contracts/templates/{contract_template_b.id}/')
        assert r.status_code == 404

    def test_template_update_other_org_returns_404(self, client_a, contract_template_b):
        r = client_a.patch(
            f'/api/v1/contracts/templates/{contract_template_b.id}/',
            {'is_active': False}, format='json',
        )
        assert r.status_code == 404

    def test_records_exclude_other_org(self, client_a, contract_a, contract_b):
        r = client_a.get('/api/v1/contracts/records/')
        ids = [x['id'] for x in r.data['results']]
        assert str(contract_a.id) in ids
        assert str(contract_b.id) not in ids

    def test_record_retrieve_other_org_returns_404(self, client_a, contract_b):
        r = client_a.get(f'/api/v1/contracts/records/{contract_b.id}/')
        assert r.status_code == 404

    def test_record_update_other_org_returns_404(self, client_a, contract_b):
        r = client_a.patch(
            f'/api/v1/contracts/records/{contract_b.id}/',
            {'notes': 'Hacked'}, format='json',
        )
        assert r.status_code == 404

    def test_issue_other_org_record_returns_404(self, client_a, contract_b):
        r = client_a.post(
            f'/api/v1/contracts/records/{contract_b.id}/issue/', {}, format='json',
        )
        assert r.status_code == 404

    def test_signatures_exclude_other_org(self, client_a, signature_a, signature_b):
        r = client_a.get('/api/v1/contracts/signatures/')
        ids = [x['id'] for x in r.data['results']]
        assert str(signature_a.id) in ids
        assert str(signature_b.id) not in ids

    def test_signature_retrieve_other_org_returns_404(self, client_a, signature_b):
        r = client_a.get(f'/api/v1/contracts/signatures/{signature_b.id}/')
        assert r.status_code == 404

    def test_sign_other_org_signature_returns_404(self, client_a, signature_b):
        r = client_a.post(
            f'/api/v1/contracts/signatures/{signature_b.id}/sign/', {}, format='json',
        )
        assert r.status_code == 404


@pytest.mark.django_db
class TestSuppliersTenantIsolation:
    def test_suppliers_exclude_other_org(self, client_a, supplier_a, supplier_b):
        r = client_a.get('/api/v1/suppliers/')
        ids = [x['id'] for x in r.data['results']]
        assert str(supplier_a.id) in ids
        assert str(supplier_b.id) not in ids

    def test_supplier_retrieve_other_org_returns_404(self, client_a, supplier_b):
        r = client_a.get(f'/api/v1/suppliers/{supplier_b.id}/')
        assert r.status_code == 404

    def test_supplier_update_other_org_returns_404(self, client_a, supplier_b):
        r = client_a.patch(f'/api/v1/suppliers/{supplier_b.id}/', {'name': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_verify_other_org_supplier_returns_404(self, client_a, supplier_b):
        r = client_a.post(f'/api/v1/suppliers/{supplier_b.id}/verify/', {}, format='json')
        assert r.status_code == 404

    def test_supplier_docs_exclude_other_org(self, client_a, org_a, org_b, supplier_a, supplier_b):
        from apps.suppliers.models import SupplierDocument
        doc_a = SupplierDocument.objects.create(
            organisation=org_a, supplier=supplier_a, document_type='csd_report',
        )
        doc_b = SupplierDocument.objects.create(
            organisation=org_b, supplier=supplier_b, document_type='csd_report',
        )
        r = client_a.get('/api/v1/suppliers/documents/')
        ids = [x['id'] for x in r.data['results']]
        assert str(doc_a.id) in ids
        assert str(doc_b.id) not in ids

    def test_engagements_exclude_other_org(self, client_a, supplier_engagement_a, supplier_engagement_b):
        r = client_a.get('/api/v1/suppliers/engagements/')
        ids = [x['id'] for x in r.data['results']]
        assert str(supplier_engagement_a.id) in ids
        assert str(supplier_engagement_b.id) not in ids

    def test_engagement_retrieve_other_org_returns_404(self, client_a, supplier_engagement_b):
        r = client_a.get(f'/api/v1/suppliers/engagements/{supplier_engagement_b.id}/')
        assert r.status_code == 404

    def test_payment_packs_exclude_other_org(self, client_a, org_a, org_b,
                                              supplier_engagement_a, supplier_engagement_b,
                                              context_a, context_b):
        from apps.suppliers.models import PaymentPack
        pack_a = PaymentPack.objects.create(
            organisation=org_a, supplier_engagement=supplier_engagement_a,
            operating_context=context_a, amount='1000',
        )
        pack_b = PaymentPack.objects.create(
            organisation=org_b, supplier_engagement=supplier_engagement_b,
            operating_context=context_b, amount='2000',
        )
        r = client_a.get('/api/v1/suppliers/payment-packs/')
        ids = [x['id'] for x in r.data['results']]
        assert str(pack_a.id) in ids
        assert str(pack_b.id) not in ids

    def test_payment_pack_retrieve_other_org_returns_404(self, client_a, org_b,
                                                          supplier_engagement_b, context_b):
        from apps.suppliers.models import PaymentPack
        pack = PaymentPack.objects.create(
            organisation=org_b, supplier_engagement=supplier_engagement_b,
            operating_context=context_b, amount='500',
        )
        r = client_a.get(f'/api/v1/suppliers/payment-packs/{pack.id}/')
        assert r.status_code == 404


@pytest.mark.django_db
class TestArtistsTenantIsolation:
    def test_artists_exclude_other_org(self, client_a, artist_a, artist_b):
        r = client_a.get('/api/v1/artists/')
        ids = [x['id'] for x in r.data['results']]
        assert str(artist_a.id) in ids
        assert str(artist_b.id) not in ids

    def test_artist_retrieve_other_org_returns_404(self, client_a, artist_b):
        r = client_a.get(f'/api/v1/artists/{artist_b.id}/')
        assert r.status_code == 404

    def test_artist_update_other_org_returns_404(self, client_a, artist_b):
        r = client_a.patch(f'/api/v1/artists/{artist_b.id}/', {'notes': 'Hacked'}, format='json')
        assert r.status_code == 404

    def test_artist_docs_exclude_other_org(self, client_a, org_a, org_b, artist_a, artist_b):
        from apps.artists.models import ArtistDocument
        doc_a = ArtistDocument.objects.create(
            organisation=org_a, artist=artist_a, document_type='id_copy',
        )
        doc_b = ArtistDocument.objects.create(
            organisation=org_b, artist=artist_b, document_type='id_copy',
        )
        r = client_a.get('/api/v1/artists/documents/')
        ids = [x['id'] for x in r.data['results']]
        assert str(doc_a.id) in ids
        assert str(doc_b.id) not in ids

    def test_artist_doc_retrieve_other_org_returns_404(self, client_a, org_b, artist_b):
        from apps.artists.models import ArtistDocument
        doc = ArtistDocument.objects.create(
            organisation=org_b, artist=artist_b, document_type='contract',
        )
        r = client_a.get(f'/api/v1/artists/documents/{doc.id}/')
        assert r.status_code == 404

    def test_engagements_exclude_other_org(self, client_a, artist_engagement_a, artist_engagement_b):
        r = client_a.get('/api/v1/artists/engagements/')
        ids = [x['id'] for x in r.data['results']]
        assert str(artist_engagement_a.id) in ids
        assert str(artist_engagement_b.id) not in ids

    def test_engagement_retrieve_other_org_returns_404(self, client_a, artist_engagement_b):
        r = client_a.get(f'/api/v1/artists/engagements/{artist_engagement_b.id}/')
        assert r.status_code == 404

    def test_confirm_other_org_engagement_returns_404(self, client_a, artist_engagement_b):
        r = client_a.post(
            f'/api/v1/artists/engagements/{artist_engagement_b.id}/confirm/',
            {}, format='json',
        )
        assert r.status_code == 404


@pytest.mark.django_db
class TestYouthTenantIsolation:
    # ── YouthProject ──────────────────────────────────────────────────────────

    def test_youth_projects_exclude_other_org(self, client_a, youth_project_a, youth_project_b):
        r = client_a.get('/api/v1/youth/projects/')
        ids = [x['id'] for x in r.data['results']]
        assert str(youth_project_a.id) in ids
        assert str(youth_project_b.id) not in ids

    def test_youth_project_retrieve_other_org_returns_404(self, client_a, youth_project_b):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_b.id}/')
        assert r.status_code == 404

    def test_youth_project_update_other_org_returns_404(self, client_a, youth_project_b):
        r = client_a.patch(
            f'/api/v1/youth/projects/{youth_project_b.id}/',
            {'target_learners': 99}, format='json',
        )
        assert r.status_code == 404

    def test_youth_project_stats_other_org_returns_404(self, client_a, youth_project_b):
        r = client_a.get(f'/api/v1/youth/projects/{youth_project_b.id}/stats/')
        assert r.status_code == 404

    # ── Activity ──────────────────────────────────────────────────────────────

    def test_activities_exclude_other_org(self, client_a, activity_a, activity_b):
        r = client_a.get('/api/v1/youth/activities/')
        ids = [x['id'] for x in r.data['results']]
        assert str(activity_a.id) in ids
        assert str(activity_b.id) not in ids

    def test_activity_retrieve_other_org_returns_404(self, client_a, activity_b):
        r = client_a.get(f'/api/v1/youth/activities/{activity_b.id}/')
        assert r.status_code == 404

    def test_activity_update_other_org_returns_404(self, client_a, activity_b):
        r = client_a.patch(
            f'/api/v1/youth/activities/{activity_b.id}/',
            {'name': 'Hacked'}, format='json',
        )
        assert r.status_code == 404

    # ── Session ───────────────────────────────────────────────────────────────

    def test_sessions_exclude_other_org(self, client_a, session_a, session_b):
        r = client_a.get('/api/v1/youth/sessions/')
        ids = [x['id'] for x in r.data['results']]
        assert str(session_a.id) in ids
        assert str(session_b.id) not in ids

    def test_session_retrieve_other_org_returns_404(self, client_a, session_b):
        r = client_a.get(f'/api/v1/youth/sessions/{session_b.id}/')
        assert r.status_code == 404

    def test_capture_attendance_other_org_returns_404(self, client_a, session_b):
        r = client_a.post(
            f'/api/v1/youth/sessions/{session_b.id}/capture-attendance/',
            {'attendance': []}, format='json',
        )
        assert r.status_code == 404

    # ── LearnerGroup ──────────────────────────────────────────────────────────

    def test_learner_groups_exclude_other_org(self, client_a, learner_group_a, learner_group_b):
        r = client_a.get('/api/v1/youth/learner-groups/')
        ids = [x['id'] for x in r.data['results']]
        assert str(learner_group_a.id) in ids
        assert str(learner_group_b.id) not in ids

    def test_learner_group_retrieve_other_org_returns_404(self, client_a, learner_group_b):
        r = client_a.get(f'/api/v1/youth/learner-groups/{learner_group_b.id}/')
        assert r.status_code == 404

    # ── FacilitatorAssignment ─────────────────────────────────────────────────

    def test_facilitators_exclude_other_org(self, client_a, org_a, org_b, youth_project_a, youth_project_b, user_a, user_b):
        from apps.youth.models import FacilitatorAssignment
        fa_a = FacilitatorAssignment.objects.create(
            organisation=org_a, youth_project=youth_project_a, facilitator=user_a, role='lead',
        )
        fa_b = FacilitatorAssignment.objects.create(
            organisation=org_b, youth_project=youth_project_b, facilitator=user_b, role='lead',
        )
        r = client_a.get('/api/v1/youth/facilitators/')
        ids = [x['id'] for x in r.data['results']]
        assert str(fa_a.id) in ids
        assert str(fa_b.id) not in ids

    def test_facilitator_retrieve_other_org_returns_404(self, client_a, org_b, youth_project_b, user_b):
        from apps.youth.models import FacilitatorAssignment
        fa_b = FacilitatorAssignment.objects.create(
            organisation=org_b, youth_project=youth_project_b, facilitator=user_b, role='support',
        )
        r = client_a.get(f'/api/v1/youth/facilitators/{fa_b.id}/')
        assert r.status_code == 404

    # ── ConsentRecord ─────────────────────────────────────────────────────────

    def test_consent_records_exclude_other_org(self, client_a, org_a, org_b, youth_project_a, youth_project_b):
        from apps.youth.models import ConsentRecord
        cr_a = ConsentRecord.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-A-001', guardian_consent_received=True,
        )
        cr_b = ConsentRecord.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            learner_identifier='LRN-B-001', guardian_consent_received=True,
        )
        r = client_a.get('/api/v1/youth/consent/')
        ids = [x['id'] for x in r.data['results']]
        assert str(cr_a.id) in ids
        assert str(cr_b.id) not in ids

    def test_consent_retrieve_other_org_returns_404(self, client_a, org_b, youth_project_b):
        from apps.youth.models import ConsentRecord
        cr = ConsentRecord.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            learner_identifier='LRN-B-002', guardian_consent_received=False,
        )
        r = client_a.get(f'/api/v1/youth/consent/{cr.id}/')
        assert r.status_code == 404

    # ── AttendanceRecord ──────────────────────────────────────────────────────

    def test_attendance_records_exclude_other_org(self, client_a, org_a, org_b, session_a, session_b):
        from apps.youth.models import AttendanceRecord
        ar_a = AttendanceRecord.objects.create(
            organisation=org_a, session=session_a, learner_identifier='LRN-A-001', present=True,
        )
        ar_b = AttendanceRecord.objects.create(
            organisation=org_b, session=session_b, learner_identifier='LRN-B-001', present=True,
        )
        r = client_a.get('/api/v1/youth/attendance/')
        ids = [x['id'] for x in r.data['results']]
        assert str(ar_a.id) in ids
        assert str(ar_b.id) not in ids

    def test_attendance_retrieve_other_org_returns_404(self, client_a, org_b, session_b):
        from apps.youth.models import AttendanceRecord
        ar = AttendanceRecord.objects.create(
            organisation=org_b, session=session_b, learner_identifier='LRN-B-002', present=False,
        )
        r = client_a.get(f'/api/v1/youth/attendance/{ar.id}/')
        assert r.status_code == 404

    # ── Assessment ────────────────────────────────────────────────────────────

    def test_assessments_exclude_other_org(self, client_a, org_a, org_b, youth_project_a, youth_project_b, user_a, user_b):
        from apps.youth.models import Assessment
        ass_a = Assessment.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            learner_identifier='LRN-A-001', assessment_type='formative',
            assessment_date='2025-03-01', assessor=user_a,
        )
        ass_b = Assessment.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            learner_identifier='LRN-B-001', assessment_type='formative',
            assessment_date='2025-03-01', assessor=user_b,
        )
        r = client_a.get('/api/v1/youth/assessments/')
        ids = [x['id'] for x in r.data['results']]
        assert str(ass_a.id) in ids
        assert str(ass_b.id) not in ids

    def test_assessment_retrieve_other_org_returns_404(self, client_a, org_b, youth_project_b, user_b):
        from apps.youth.models import Assessment
        ass = Assessment.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            learner_identifier='LRN-B-002', assessment_type='summative',
            assessment_date='2025-06-01', assessor=user_b,
        )
        r = client_a.get(f'/api/v1/youth/assessments/{ass.id}/')
        assert r.status_code == 404

    # ── ShowcaseOutput ────────────────────────────────────────────────────────

    def test_showcases_exclude_other_org(self, client_a, org_a, org_b, youth_project_a, youth_project_b):
        from apps.youth.models import ShowcaseOutput
        so_a = ShowcaseOutput.objects.create(
            organisation=org_a, youth_project=youth_project_a,
            title='Showcase A', output_type='performance', date='2025-06-15',
        )
        so_b = ShowcaseOutput.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            title='Showcase B', output_type='performance', date='2025-06-15',
        )
        r = client_a.get('/api/v1/youth/showcases/')
        ids = [x['id'] for x in r.data['results']]
        assert str(so_a.id) in ids
        assert str(so_b.id) not in ids

    def test_showcase_retrieve_other_org_returns_404(self, client_a, org_b, youth_project_b):
        from apps.youth.models import ShowcaseOutput
        so = ShowcaseOutput.objects.create(
            organisation=org_b, youth_project=youth_project_b,
            title='Showcase B', output_type='exhibition', date='2025-07-01',
        )
        r = client_a.get(f'/api/v1/youth/showcases/{so.id}/')
        assert r.status_code == 404
