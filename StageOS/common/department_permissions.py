from common.permissions import UserRoles, is_admin_user
from apps.structure.models import AuthorityLevel, ModuleActivation, UserDepartmentMembership


INTERNAL_MODULES = {
    'dashboard',
    'calendar',
    'workspaces',
    'programming',
    'marketing',
    'technical',
    'operations',
    'contracts',
    'suppliers',
    'artists',
    'ticketing',
    'youth',
    'governance',
    'hospitality',
    'documents',
    'reports',
    'audit',
    'settings',
}


def user_department_memberships(user):
    if not getattr(user, 'is_authenticated', False) or not getattr(user, 'organisation_id', None):
        return UserDepartmentMembership.objects.none()
    return (
        UserDepartmentMembership.objects
        .filter(user=user, organisation_id=user.organisation_id, is_active=True)
        .select_related('department', 'position', 'site')
    )


def has_department_membership(user):
    return user_department_memberships(user).exists()


def user_departments(user):
    return [membership.department for membership in user_department_memberships(user)]


def user_primary_department(user):
    membership = user_department_memberships(user).filter(is_primary=True).first()
    return membership.department if membership else None


def user_positions(user):
    return [membership.position for membership in user_department_memberships(user)]


def user_primary_position(user):
    membership = user_department_memberships(user).filter(is_primary=True).first()
    return membership.position if membership else None


def _department_id(department):
    return getattr(department, 'id', department)


def _membership_for(user, department):
    if not department:
        return None
    return user_department_memberships(user).filter(department_id=_department_id(department)).first()


def _user_type(user):
    return getattr(user, 'user_type', None)


def _is_executive(user):
    return _user_type(user) == UserRoles.EXECUTIVE


def _is_gm(user):
    return user_department_memberships(user).filter(authority_level=AuthorityLevel.GM).exists()


def is_department_manager(user, department):
    membership = _membership_for(user, department)
    return bool(membership and membership.authority_level == AuthorityLevel.DEPARTMENT_MANAGER)


def is_department_user(user, department):
    membership = _membership_for(user, department)
    return bool(membership and membership.authority_level == AuthorityLevel.DEPARTMENT_USER)


def is_department_specialist(user, department):
    membership = _membership_for(user, department)
    return bool(membership and membership.authority_level == AuthorityLevel.SPECIALIST)


def can_manage_department(user, department):
    if is_admin_user(user):
        return True
    membership = _membership_for(user, department)
    return bool(membership and membership.can_manage_department)


def can_assign_department_work(user, department):
    if is_admin_user(user):
        return True
    membership = _membership_for(user, department)
    return bool(membership and membership.can_assign_work)


def can_approve_department_work(user, department):
    if is_admin_user(user) or _is_executive(user):
        return True
    membership = _membership_for(user, department)
    return bool(membership and membership.can_approve_work)


def can_view_department_summary(user, department):
    if is_admin_user(user) or _is_executive(user) or _is_gm(user):
        return True
    membership = _membership_for(user, department)
    return bool(membership and membership.can_view_department_summary)


def can_raise_department_issue(user, department):
    if is_admin_user(user) or _is_executive(user):
        return True
    membership = _membership_for(user, department)
    return bool(membership and membership.can_raise_department_issue)


def can_view_sensitive_department_data(user, department):
    membership = _membership_for(user, department)
    return bool(is_admin_user(user) or _is_executive(user) or (membership and membership.can_manage_department))


def can_access_module(user, module_key):
    if not getattr(user, 'is_authenticated', False) or not getattr(user, 'organisation_id', None):
        return False
    if is_admin_user(user) and module_key in INTERNAL_MODULES:
        return True
    if _user_type(user) in {UserRoles.CLIENT_EXTERNAL, UserRoles.SUPPLIER_EXTERNAL, UserRoles.ARTIST_EXTERNAL}:
        return False
    return ModuleActivation.objects.filter(
        organisation_id=user.organisation_id,
        module_key=module_key,
        is_enabled=True,
    ).exists()
