from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User, UserType
from apps.organisations.models import Organisation
from apps.structure.models import (
    ApprovalPolicy,
    AuthorityLevel,
    Department,
    EvidenceRule,
    ModuleActivation,
    OrganisationOperatingModel,
    Position,
    SOPTemplate,
    Site,
    UserDepartmentMembership,
)
from common import department_permissions


PASSWORD = 'MoukangweTest123!'
ORG_SLUG = 'moukangwe-theatre'


def seed():
    call_command('seed_dev_data', stdout=StringIO())


def auth_client(email):
    user = User.objects.get(email=email)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_operating_model_foundation_models_can_be_created(org_a, department_a):
    operating_model = OrganisationOperatingModel.objects.create(
        organisation=org_a,
        name='Configurable Model',
        model_type='custom',
    )
    position = Position.objects.create(
        organisation=org_a,
        department=department_a,
        title='Marketing Manager',
        level='manager',
        authority_level=AuthorityLevel.DEPARTMENT_MANAGER,
        is_manager_position=True,
    )
    user = User.objects.create_user('manager@example.com', 'testpass123', organisation=org_a, user_type=UserType.MANAGER)
    membership = UserDepartmentMembership.objects.create(
        organisation=org_a,
        user=user,
        department=department_a,
        position=position,
        authority_level=AuthorityLevel.DEPARTMENT_MANAGER,
        is_primary=True,
        can_manage_department=True,
        can_assign_work=True,
        can_approve_work=True,
    )
    module = ModuleActivation.objects.create(organisation=org_a, module_key='marketing', label='Marketing')
    policy = ApprovalPolicy.objects.create(
        organisation=org_a,
        department=department_a,
        module_key='marketing',
        approval_scope='marketing_readiness',
        required_authority_level=AuthorityLevel.DEPARTMENT_MANAGER,
    )
    rule = EvidenceRule.objects.create(
        organisation=org_a,
        department=department_a,
        module_key='marketing',
        record_type='department_work',
        reviewer_authority_level=AuthorityLevel.DEPARTMENT_MANAGER,
    )
    sop = SOPTemplate.objects.create(
        organisation=org_a,
        operating_model=operating_model,
        workspace_type='production',
        department=department_a,
        title='Marketing SOP',
    )

    assert operating_model.pk
    assert position.pk
    assert membership.pk
    assert module.pk
    assert policy.pk
    assert rule.pk
    assert sop.pk
    assert department_permissions.user_primary_department(user) == department_a
    assert department_permissions.user_primary_position(user) == position


@pytest.mark.django_db
def test_department_permission_helpers_distinguish_manager_authority():
    seed()
    marketing = Department.objects.get(organisation__slug=ORG_SLUG, name='Marketing and Communications')
    technical = Department.objects.get(organisation__slug=ORG_SLUG, name='Technical and Stage Management')
    marketing_manager = User.objects.get(email='marketing.manager@moukangwetheatre.test')
    technical_manager = User.objects.get(email='technical.manager@moukangwetheatre.test')
    board = User.objects.get(email='board@moukangwetheatre.test')
    client = User.objects.get(email='client@moukangwetheatre.test')
    executive = User.objects.get(email='ceo@moukangwetheatre.test')

    assert department_permissions.is_department_manager(marketing_manager, marketing)
    assert department_permissions.can_manage_department(marketing_manager, marketing)
    assert department_permissions.can_assign_department_work(marketing_manager, marketing)
    assert department_permissions.can_approve_department_work(marketing_manager, marketing)
    assert not department_permissions.can_manage_department(marketing_manager, technical)
    assert not department_permissions.can_approve_department_work(marketing_manager, technical)
    assert department_permissions.can_manage_department(technical_manager, technical)
    assert not department_permissions.can_approve_department_work(technical_manager, marketing)
    assert not department_permissions.can_manage_department(board, marketing)
    assert not department_permissions.can_manage_department(client, marketing)
    assert department_permissions.can_view_department_summary(executive, technical)


@pytest.mark.django_db
def test_seed_dev_data_maps_required_uat_users_and_templates_idempotently():
    seed()
    counts = {
        'positions': Position.objects.filter(organisation__slug=ORG_SLUG).count(),
        'memberships': UserDepartmentMembership.objects.filter(organisation__slug=ORG_SLUG).count(),
        'models': OrganisationOperatingModel.objects.filter(organisation__slug=ORG_SLUG).count(),
    }
    seed()
    org = Organisation.objects.get(slug=ORG_SLUG)
    site = Site.objects.get(organisation=org, name='Moukangwe Theatre Complex')
    marketing = Department.objects.get(organisation=org, name='Marketing and Communications')
    technical = Department.objects.get(organisation=org, name='Technical and Stage Management')

    assert Position.objects.filter(organisation=org, title='Marketing Manager', department=marketing).exists()
    assert Position.objects.filter(organisation=org, title='Technical Manager', department=technical).exists()
    assert User.objects.get(email='marketing.manager@moukangwetheatre.test').check_password(PASSWORD)
    assert UserDepartmentMembership.objects.get(
        organisation=org,
        user__email='marketing.manager@moukangwetheatre.test',
        department=marketing,
        position__title='Marketing Manager',
        site=site,
        authority_level=AuthorityLevel.DEPARTMENT_MANAGER,
    ).can_manage_department
    assert UserDepartmentMembership.objects.get(user__email='designer@moukangwetheatre.test').department == marketing
    assert UserDepartmentMembership.objects.get(user__email='technical.manager@moukangwetheatre.test').department == technical
    assert UserDepartmentMembership.objects.get(user__email='foh.manager@moukangwetheatre.test').authority_level == AuthorityLevel.DEPARTMENT_MANAGER
    assert UserDepartmentMembership.objects.get(user__email='board@moukangwetheatre.test').authority_level == AuthorityLevel.READ_ONLY
    assert UserDepartmentMembership.objects.get(user__email='client@moukangwetheatre.test').authority_level == AuthorityLevel.EXTERNAL
    assert UserDepartmentMembership.objects.get(user__email='supplier@moukangwetheatre.test').authority_level == AuthorityLevel.EXTERNAL
    assert UserDepartmentMembership.objects.get(user__email='artist@moukangwetheatre.test').authority_level == AuthorityLevel.EXTERNAL
    assert OrganisationOperatingModel.objects.filter(organisation=org, name='JCT Multi-Theatre Operating Model').exists()
    assert OrganisationOperatingModel.objects.filter(organisation=org, name='State Theatre Institutional Operating Model').exists()
    assert ModuleActivation.objects.filter(organisation=org, module_key='dashboard', is_enabled=True).exists()
    assert Position.objects.filter(organisation=org).count() == counts['positions']
    assert UserDepartmentMembership.objects.filter(organisation=org).count() == counts['memberships']
    assert OrganisationOperatingModel.objects.filter(organisation=org).count() == counts['models']


@pytest.mark.django_db
def test_operating_profile_api_returns_department_position_and_permissions():
    seed()
    client = auth_client('marketing.manager@moukangwetheatre.test')
    response = client.get('/api/v1/me/operating-profile/')

    assert response.status_code == 200
    assert response.data['user']['email'] == 'marketing.manager@moukangwetheatre.test'
    assert response.data['organisation']['name'] == 'Moukangwe Theatre'
    assert response.data['primary_department']['name'] == 'Marketing and Communications'
    assert response.data['primary_position']['title'] == 'Marketing Manager'
    assert response.data['primary_position']['authority_level'] == AuthorityLevel.DEPARTMENT_MANAGER
    assert [item['name'] for item in response.data['can_manage_departments']] == ['Marketing and Communications']
    assert [item['name'] for item in response.data['can_approve_departments']] == ['Marketing and Communications']
    assert 'dashboard' in response.data['active_modules']


@pytest.mark.django_db
def test_admin_can_list_configuration_and_read_only_or_external_cannot_mutate():
    seed()
    admin_response = auth_client('admin@moukangwetheatre.test').get('/api/v1/operating-models/')
    assert admin_response.status_code == 200
    assert admin_response.data['count'] >= 3

    readonly_response = auth_client('board@moukangwetheatre.test').post(
        '/api/v1/module-activations/',
        {'module_key': 'test', 'label': 'Test', 'is_enabled': True},
        format='json',
    )
    external_response = auth_client('client@moukangwetheatre.test').post(
        '/api/v1/module-activations/',
        {'module_key': 'test', 'label': 'Test', 'is_enabled': True},
        format='json',
    )
    assert readonly_response.status_code == 403
    assert external_response.status_code == 403


@pytest.mark.django_db
def test_wrong_tenant_cannot_access_another_operating_model(client_a, org_b):
    other_model = OrganisationOperatingModel.objects.create(
        organisation=org_b,
        name='Other Model',
        model_type='single_venue',
    )
    response = client_a.get(f'/api/v1/operating-models/{other_model.id}/')
    assert response.status_code == 404
