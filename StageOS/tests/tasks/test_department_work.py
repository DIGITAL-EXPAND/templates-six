from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.contexts.models import OperatingContext
from apps.structure.models import Department
from apps.tasks.models import Notification, Task


PASSWORD = 'MoukangweTest123!'
ORG_SLUG = 'moukangwe-theatre'


def seed():
    call_command('seed_dev_data', stdout=StringIO())


def client_for(email):
    user = User.objects.get(email=email)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_department_manager_can_assign_own_department_work_and_notification_is_created():
    seed()
    client, manager = client_for('marketing.manager@moukangwetheatre.test')
    org = manager.organisation
    workspace = OperatingContext.objects.filter(organisation=org).first()
    department = Department.objects.get(organisation=org, name='Marketing and Communications')
    assignee = User.objects.get(email='marketing.user@moukangwetheatre.test')

    response = client.post('/api/v1/tasks/', {
        'operating_context': str(workspace.id),
        'title': 'Prepare campaign checklist',
        'department': str(department.id),
        'assigned_to': str(assignee.id),
        'work_type': 'readiness',
        'priority': 'medium',
    }, format='json')

    assert response.status_code == 201
    task = Task.objects.get(id=response.data['id'])
    assert task.assigned_by == manager
    assert task.work_type == 'readiness'
    assert Notification.objects.filter(recipient=assignee, task=task, notification_type='task_assigned').exists()


@pytest.mark.django_db
def test_department_manager_cannot_assign_other_department_work():
    seed()
    client, manager = client_for('marketing.manager@moukangwetheatre.test')
    org = manager.organisation
    workspace = OperatingContext.objects.filter(organisation=org).first()
    technical = Department.objects.get(organisation=org, name='Technical and Stage Management')
    assignee = User.objects.get(email='technical.user@moukangwetheatre.test')

    response = client.post('/api/v1/tasks/', {
        'operating_context': str(workspace.id),
        'title': 'Prepare lighting plot',
        'department': str(technical.id),
        'assigned_to': str(assignee.id),
    }, format='json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_assigned_user_can_start_and_block_own_task_but_not_cancel_it():
    seed()
    manager_client, manager = client_for('marketing.manager@moukangwetheatre.test')
    user_client, assignee = client_for('marketing.user@moukangwetheatre.test')
    org = manager.organisation
    workspace = OperatingContext.objects.filter(organisation=org).first()
    department = Department.objects.get(organisation=org, name='Marketing and Communications')
    create_response = manager_client.post('/api/v1/tasks/', {
        'operating_context': str(workspace.id),
        'title': 'Draft social copy',
        'department': str(department.id),
        'assigned_to': str(assignee.id),
    }, format='json')
    task_id = create_response.data['id']

    start_response = user_client.post(f'/api/v1/tasks/{task_id}/start/', {'comment': 'Started'}, format='json')
    block_response = user_client.post(f'/api/v1/tasks/{task_id}/block/', {'comment': 'Waiting for artwork'}, format='json')
    cancel_response = user_client.post(f'/api/v1/tasks/{task_id}/cancel/', {'comment': 'Cancel'}, format='json')

    assert start_response.status_code == 200
    assert start_response.data['status'] == 'in_progress'
    assert block_response.status_code == 200
    assert block_response.data['status'] == 'blocked'
    assert block_response.data['blocked_reason'] == 'Waiting for artwork'
    assert cancel_response.status_code == 403


@pytest.mark.django_db
def test_notifications_are_scoped_to_recipient_and_can_be_marked_read():
    seed()
    manager_client, manager = client_for('marketing.manager@moukangwetheatre.test')
    user_client, assignee = client_for('marketing.user@moukangwetheatre.test')
    other_client, _ = client_for('technical.user@moukangwetheatre.test')
    org = manager.organisation
    workspace = OperatingContext.objects.filter(organisation=org).first()
    department = Department.objects.get(organisation=org, name='Marketing and Communications')
    create_response = manager_client.post('/api/v1/tasks/', {
        'operating_context': str(workspace.id),
        'title': 'Review press release',
        'department': str(department.id),
        'assigned_to': str(assignee.id),
    }, format='json')

    user_notifications = user_client.get('/api/v1/notifications/')
    other_notifications = other_client.get('/api/v1/notifications/')
    notification_id = user_notifications.data['results'][0]['id']
    mark_read = user_client.post(f'/api/v1/notifications/{notification_id}/mark_read/')

    assert create_response.status_code == 201
    assert user_notifications.status_code == 200
    assert user_notifications.data['count'] >= 1
    assert other_notifications.status_code == 200
    assert all(item['task'] != create_response.data['id'] for item in other_notifications.data['results'])
    assert mark_read.status_code == 200
    assert mark_read.data['read_at'] is not None
