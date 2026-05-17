from rest_framework import serializers


def check_tenant_fk(value, request, label):
    """Raise ValidationError if a related object belongs to a different organisation.

    Handles None (nullable FKs pass through) and objects with no organisation_id
    (e.g. superuser as owner) transparently.
    """
    if value is None or request is None:
        return value
    obj_org_id = getattr(value, 'organisation_id', None)
    if obj_org_id is not None and obj_org_id != request.user.organisation_id:
        raise serializers.ValidationError(f'{label} does not belong to your organisation.')
    return value


def validate_unique_context(serializer_instance, value):
    """Validate that operating_context is unique for one-per-context models (OneToOneField)."""
    qs = serializer_instance.Meta.model.objects.filter(operating_context=value)
    if serializer_instance.instance:
        qs = qs.exclude(pk=serializer_instance.instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            'A record already exists for this operating context.'
        )
    return value


class ProtectedFieldsMixin:
    protected_fields = ()

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method in {'POST', 'PUT', 'PATCH'}:
            protected = set(self.protected_fields).intersection(self.initial_data.keys())
            if protected:
                raise serializers.ValidationError({
                    field: 'This field is controlled by a business action endpoint.'
                    for field in sorted(protected)
                })
        return super().validate(attrs)


def require_non_negative(attrs, fields):
    errors = {}
    for field in fields:
        value = attrs.get(field)
        if value is not None and value < 0:
            errors[field] = 'Value cannot be negative.'
    if errors:
        raise serializers.ValidationError(errors)


def require_ordered_dates(attrs, start_field, end_field, message=None):
    start = attrs.get(start_field)
    end = attrs.get(end_field)
    if start and end and end < start:
        raise serializers.ValidationError({
            end_field: message or f'{end_field} cannot be before {start_field}.'
        })
