from rest_framework import serializers
from common.permissions import is_manager_or_admin, UserRoles
from common import department_permissions
from apps.structure.models import ModuleActivation
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'user_type', 'is_active', 'date_joined']
        read_only_fields = ['id', 'user_type', 'is_active', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'user_type']

    def validate_user_type(self, value):
        request = self.context.get('request')
        if not request or not is_manager_or_admin(request.user):
            raise serializers.ValidationError('You are not allowed to assign user roles.')
        allowed = {
            UserRoles.EXECUTIVE,
            UserRoles.MANAGER,
            UserRoles.STAFF,
            UserRoles.READ_ONLY,
            UserRoles.SUPPLIER_EXTERNAL,
            UserRoles.ARTIST_EXTERNAL,
            UserRoles.CLIENT_EXTERNAL,
            UserRoles.YOUTH_EXTERNAL,
            UserRoles.INTEGRATION_SERVICE,
        }
        if getattr(request.user, 'user_type', None) == UserRoles.INTERNAL_ADMIN:
            allowed.add(UserRoles.INTERNAL_ADMIN)
        if value not in allowed:
            raise serializers.ValidationError('You are not allowed to assign this user type.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


def _department_payload(department):
    if not department:
        return None
    return {
        'id': str(department.id),
        'name': department.name,
        'code': department.code,
    }


def _position_payload(position):
    if not position:
        return None
    return {
        'id': str(position.id),
        'title': position.title,
        'authority_level': position.authority_level,
    }


class OperatingProfileSerializer(serializers.Serializer):
    def to_representation(self, user):
        memberships = list(department_permissions.user_department_memberships(user))
        primary_membership = next((item for item in memberships if item.is_primary), memberships[0] if memberships else None)
        active_modules = list(
            ModuleActivation.objects
            .filter(organisation_id=user.organisation_id, is_enabled=True)
            .order_by('module_key')
            .values_list('module_key', flat=True)
        ) if getattr(user, 'organisation_id', None) else []
        return {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'user_type': user.user_type,
            },
            'organisation': {
                'id': str(user.organisation_id),
                'name': user.organisation.name,
            } if getattr(user, 'organisation_id', None) else None,
            'primary_site': {
                'id': str(primary_membership.site.id),
                'name': primary_membership.site.name,
            } if primary_membership and primary_membership.site else None,
            'primary_department': _department_payload(primary_membership.department if primary_membership else None),
            'primary_position': _position_payload(primary_membership.position if primary_membership else None),
            'memberships': [
                {
                    'id': str(membership.id),
                    'site': {'id': str(membership.site.id), 'name': membership.site.name} if membership.site else None,
                    'department': _department_payload(membership.department),
                    'position': _position_payload(membership.position),
                    'authority_level': membership.authority_level,
                    'is_primary': membership.is_primary,
                    'can_manage_department': membership.can_manage_department,
                    'can_assign_work': membership.can_assign_work,
                    'can_approve_work': membership.can_approve_work,
                    'can_view_department_summary': membership.can_view_department_summary,
                    'can_raise_department_issue': membership.can_raise_department_issue,
                }
                for membership in memberships
            ],
            'can_manage_departments': [
                _department_payload(membership.department)
                for membership in memberships
                if membership.can_manage_department
            ],
            'can_approve_departments': [
                _department_payload(membership.department)
                for membership in memberships
                if membership.can_approve_work
            ],
            'active_modules': active_modules,
        }


# ── Leave Requests ────────────────────────────────────────────────────────────

from .models import LeaveRequest  # noqa: E402


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'leave_type', 'status', 'start_date', 'end_date',
            'days_requested', 'reason', 'approved_by', 'approved_at',
            'declined_reason', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'approved_by', 'approved_at', 'declined_reason',
            'created_at', 'updated_at',
        ]
