from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.approvals.models import ApprovalRequest, ApprovalRoute, ApprovalStep
from apps.contexts.models import OperatingContext
from apps.structure.models import Department


def seed():
    call_command('seed_dev_data', stdout=StringIO())


def client_for(email):
    user = User.objects.get(email=email)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_role_based_dashboard_kinds_and_navigation_are_distinct():
    seed()
    cases = {
        'admin@moukangwetheatre.test': 'admin',
        'ceo@moukangwetheatre.test': 'executive',
        'gm@moukangwetheatre.test': 'gm',
        'marketing.manager@moukangwetheatre.test': 'marketing',
        'designer@moukangwetheatre.test': 'marketing',
        'technical.manager@moukangwetheatre.test': 'technical',
        'foh.manager@moukangwetheatre.test': 'foh',
        'board@moukangwetheatre.test': 'board',
        'client@moukangwetheatre.test': 'client',
        'supplier@moukangwetheatre.test': 'supplier',
        'artist@moukangwetheatre.test': 'artist',
    }
    for email, expected in cases.items():
        client, _ = client_for(email)
        response = client.get('/api/v1/me/dashboard/')
        assert response.status_code == 200
        assert response.data['dashboard_kind'] == expected

    admin_nav = client_for('admin@moukangwetheatre.test')[0].get('/api/v1/me/navigation/').data['items']
    marketing_nav = client_for('marketing.manager@moukangwetheatre.test')[0].get('/api/v1/me/navigation/').data['items']
    designer_nav = client_for('designer@moukangwetheatre.test')[0].get('/api/v1/me/navigation/').data['items']
    board_nav = client_for('board@moukangwetheatre.test')[0].get('/api/v1/me/navigation/').data['items']
    client_nav = client_for('client@moukangwetheatre.test')[0].get('/api/v1/me/navigation/').data['items']

    assert 'Settings' in admin_nav
    assert 'Settings' not in marketing_nav
    assert 'Technical' not in marketing_nav
    assert designer_nav == ['Dashboard', 'My Work', 'Documents & Evidence', 'Notifications']
    assert 'Reports' in board_nav and 'Settings' not in board_nav
    assert 'Audit Trail' not in client_nav and 'Workspaces' not in client_nav


@pytest.mark.django_db
def test_private_intake_is_hidden_from_marketing_and_visible_to_programming_and_client_own_requests():
    seed()
    assert client_for('programming.manager@moukangwetheatre.test')[0].get('/api/v1/programming/intake-requests/').status_code == 200
    assert client_for('marketing.manager@moukangwetheatre.test')[0].get('/api/v1/programming/intake-requests/').status_code == 403
    client_response = client_for('client@moukangwetheatre.test')[0].get('/api/v1/programming/intake-requests/')
    assert client_response.status_code == 200
    assert all(item['contact_email'] == 'client@moukangwetheatre.test' for item in client_response.data['results'])


@pytest.mark.django_db
def test_department_task_lists_are_scoped_by_operating_model_authority():
    seed()
    marketing_response = client_for('marketing.manager@moukangwetheatre.test')[0].get('/api/v1/tasks/')
    designer_response = client_for('designer@moukangwetheatre.test')[0].get('/api/v1/tasks/')
    technical_tasks = [
        item for item in marketing_response.data['results']
        if item['department'] and Department.objects.get(id=item['department']).name == 'Technical and Stage Management'
    ]
    assert marketing_response.status_code == 200
    assert designer_response.status_code == 200
    assert technical_tasks == []


@pytest.mark.django_db
def test_department_approval_authority_is_department_specific():
    seed()
    org = User.objects.get(email='admin@moukangwetheatre.test').organisation
    workspace = OperatingContext.objects.filter(organisation=org).first()
    technical = Department.objects.get(organisation=org, name='Technical and Stage Management')
    route, _ = ApprovalRoute.objects.update_or_create(
        organisation=org,
        name='Technical Sprint 3 Route',
        defaults={'context_type': 'production', 'is_active': True},
    )
    step, _ = ApprovalStep.objects.update_or_create(
        organisation=org,
        route=route,
        step_number=9,
        defaults={'name': 'Technical readiness', 'approver_department': technical},
    )
    request, _ = ApprovalRequest.objects.update_or_create(
        organisation=org,
        operating_context=workspace,
        approval_step=step,
        defaults={'requested_by': User.objects.get(email='technical.user@moukangwetheatre.test'), 'decision': 'pending'},
    )

    marketing_response = client_for('marketing.manager@moukangwetheatre.test')[0].post(
        f'/api/v1/approvals/requests/{request.id}/approve/',
        {'comment': 'Wrong department'},
        format='json',
    )
    board_response = client_for('board@moukangwetheatre.test')[0].post(
        f'/api/v1/approvals/requests/{request.id}/reject/',
        {'comment': 'Board cannot decide'},
        format='json',
    )
    technical_response = client_for('technical.manager@moukangwetheatre.test')[0].post(
        f'/api/v1/approvals/requests/{request.id}/approve/',
        {'comment': 'Technical approved'},
        format='json',
    )

    assert marketing_response.status_code == 403
    assert technical_response.status_code == 200
    assert board_response.status_code == 403
