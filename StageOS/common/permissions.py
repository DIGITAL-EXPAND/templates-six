from rest_framework import permissions


class UserRoles:
    INTERNAL_ADMIN = 'internal_admin'
    EXECUTIVE = 'executive'
    MANAGER = 'manager'
    STAFF = 'staff'
    READ_ONLY = 'read_only'
    SUPPLIER_EXTERNAL = 'supplier_external'
    ARTIST_EXTERNAL = 'artist_external'
    CLIENT_EXTERNAL = 'client_external'
    YOUTH_EXTERNAL = 'youth_external'
    INTEGRATION_SERVICE = 'integration_service'


INTERNAL_USER_TYPES = {
    UserRoles.INTERNAL_ADMIN,
    UserRoles.EXECUTIVE,
    UserRoles.MANAGER,
    UserRoles.STAFF,
    UserRoles.READ_ONLY,
}

MUTATING_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


def user_type(user):
    return getattr(user, 'user_type', None)


def is_internal_user(user):
    return bool(user and user.is_authenticated and user_type(user) in INTERNAL_USER_TYPES)


def is_admin_user(user):
    return bool(
        user
        and user.is_authenticated
        and (getattr(user, 'is_superuser', False) or user_type(user) == UserRoles.INTERNAL_ADMIN)
    )


def is_manager_or_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (
            getattr(user, 'is_superuser', False)
            or user_type(user) in {UserRoles.INTERNAL_ADMIN, UserRoles.MANAGER}
        )
    )


def is_reporting_user(user):
    return bool(
        user
        and user.is_authenticated
        and user_type(user) in {
            UserRoles.INTERNAL_ADMIN,
            UserRoles.EXECUTIVE,
            UserRoles.MANAGER,
            UserRoles.READ_ONLY,
        }
    )


def is_executive_intervention_user(user):
    return bool(
        user
        and user.is_authenticated
        and user_type(user) in {
            UserRoles.INTERNAL_ADMIN,
            UserRoles.EXECUTIVE,
            UserRoles.MANAGER,
        }
    )


def can_decide_approval(user):
    return is_executive_intervention_user(user)


def is_read_only_user(user):
    return user_type(user) == UserRoles.READ_ONLY


def can_access_private_intake(user):
    if not user or not user.is_authenticated:
        return False
    if user_type(user) == UserRoles.CLIENT_EXTERNAL:
        return True
    if user_type(user) in {UserRoles.INTERNAL_ADMIN, UserRoles.EXECUTIVE}:
        return True
    try:
        from common.department_permissions import user_department_memberships
        memberships = user_department_memberships(user)
        if memberships.exists():
            return memberships.filter(department__department_type='programming').exists()
    except Exception:
        return False
    return user_type(user) in {UserRoles.MANAGER, UserRoles.STAFF}


class IsTenantMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.organisation_id)


class IsInternalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_internal_user(request.user)


class IsInternalMutableUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not is_internal_user(request.user):
            return False
        if request.method in MUTATING_METHODS and is_read_only_user(request.user):
            return False
        return True


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_manager_or_admin(request.user)


class CanAccessReports(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_reporting_user(request.user)


class CanAccessAudit(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_manager_or_admin(request.user) or user_type(request.user) == UserRoles.EXECUTIVE


class CanAccessYouthSensitiveData(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_internal_user(request.user) and not is_read_only_user(request.user)


class CanAccessSupplierData(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_internal_user(request.user):
            return not (request.method in MUTATING_METHODS and is_read_only_user(request.user))
        if user_type(request.user) == UserRoles.SUPPLIER_EXTERNAL:
            return request.method not in MUTATING_METHODS
        return False


class CanAccessArtistData(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_internal_user(request.user):
            return not (request.method in MUTATING_METHODS and is_read_only_user(request.user))
        if user_type(request.user) == UserRoles.ARTIST_EXTERNAL:
            return request.method not in MUTATING_METHODS
        return False


class CanAccessContracts(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_internal_user(request.user)


class CanAccessFinance(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_manager_or_admin(request.user) or user_type(request.user) == UserRoles.EXECUTIVE


class CanAccessGovernance(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_internal_user(request.user)


class CanCreateExecutiveIntervention(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in {'GET', 'HEAD', 'OPTIONS'}:
            return is_internal_user(request.user)
        action = getattr(view, 'action', '')
        if action in {'acknowledge', 'complete'}:
            return is_internal_user(request.user) and not is_read_only_user(request.user)
        if action == 'cancel':
            return is_executive_intervention_user(request.user)
        return is_executive_intervention_user(request.user)


class CanDecideApproval(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in {'GET', 'HEAD', 'OPTIONS'}:
            return is_internal_user(request.user)
        action = getattr(view, 'action', '')
        if action in {
            'approve', 'reject', 'request_changes',
            'request_more_information', 'escalate', 'exception_approve',
        }:
            return can_decide_approval(request.user)
        return is_internal_user(request.user) and not is_read_only_user(request.user)


class CanAccessPrivateIntake(permissions.BasePermission):
    def has_permission(self, request, view):
        if not can_access_private_intake(request.user):
            return False
        if user_type(request.user) == UserRoles.CLIENT_EXTERNAL:
            action = getattr(view, 'action', '')
            return request.method in {'GET', 'HEAD', 'OPTIONS'} or action == 'create'
        return not (request.method in MUTATING_METHODS and is_read_only_user(request.user))
