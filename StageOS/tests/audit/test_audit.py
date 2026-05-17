import pytest
from django.core.exceptions import ValidationError
from apps.audit.models import AuditEvent


@pytest.mark.django_db
class TestAuditEventModel:
    def test_create_event(self, org_a):
        event = AuditEvent.objects.create(
            organisation=org_a,
            event_type='user.created',
            payload={'user_id': 'abc123'},
        )
        assert event.pk is not None
        assert event.event_type == 'user.created'

    def test_update_via_save_raises(self, org_a):
        event = AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        event.event_type = 'tampered'
        with pytest.raises(ValidationError):
            event.save()

    def test_delete_raises(self, org_a):
        event = AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        with pytest.raises(ValidationError):
            event.delete()

    def test_queryset_update_raises(self, org_a):
        AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        with pytest.raises(ValidationError):
            AuditEvent.objects.all().update(event_type='tampered')

    def test_queryset_delete_raises(self, org_a):
        AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        with pytest.raises(ValidationError):
            AuditEvent.objects.all().delete()

    def test_payload_defaults_to_empty_dict(self, org_a):
        event = AuditEvent.objects.create(organisation=org_a, event_type='test.event')
        assert event.payload == {}

    def test_ordered_newest_first(self, org_a):
        e1 = AuditEvent.objects.create(organisation=org_a, event_type='first')
        e2 = AuditEvent.objects.create(organisation=org_a, event_type='second')
        events = list(AuditEvent.objects.all())
        assert events[0].pk == e2.pk
        assert events[1].pk == e1.pk


@pytest.mark.django_db
class TestAuditAdminReadOnly:
    def test_admin_has_no_add_permission(self):
        from apps.audit.admin import AuditEventAdmin
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        admin = AuditEventAdmin(AuditEvent, AdminSite())
        request = MagicMock()
        assert admin.has_add_permission(request) is False
        assert admin.has_change_permission(request) is False
        assert admin.has_delete_permission(request) is False
