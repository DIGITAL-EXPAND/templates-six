import pytest


@pytest.mark.django_db
class TestValidationAndStatusProtection:
    def test_negative_context_budget_rejected(self, client_a, site_a, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Bad budget',
            'context_type': 'production',
            'site': str(site_a.id),
            'owner': str(user_a.id),
            'budget': '-1.00',
        }, format='json')
        assert r.status_code == 400

    def test_invalid_context_date_order_rejected(self, client_a, site_a, user_a):
        r = client_a.post('/api/v1/contexts/', {
            'title': 'Bad dates',
            'context_type': 'production',
            'site': str(site_a.id),
            'owner': str(user_a.id),
            'start_date': '2026-05-10',
            'end_date': '2026-05-09',
        }, format='json')
        assert r.status_code == 400

    def test_negative_contract_value_rejected(self, client_a, context_a):
        r = client_a.post('/api/v1/contracts/records/', {
            'operating_context': str(context_a.id),
            'contract_type': 'artist',
            'counterparty_name': 'Counterparty',
            'counterparty_type': 'artist',
            'value': '-1.00',
        }, format='json')
        assert r.status_code == 400

    def test_negative_payment_amount_rejected(self, client_a, supplier_engagement_a, context_a):
        r = client_a.post('/api/v1/suppliers/payment-packs/', {
            'supplier_engagement': str(supplier_engagement_a.id),
            'operating_context': str(context_a.id),
            'amount': '-1.00',
        }, format='json')
        assert r.status_code == 400

    def test_direct_task_status_patch_rejected(self, client_a, task_a):
        r = client_a.patch(f'/api/v1/tasks/{task_a.id}/', {'status': 'done'}, format='json')
        assert r.status_code == 400

    def test_task_action_still_creates_audit(self, client_a, task_a):
        from apps.audit.models import AuditEvent

        r = client_a.post(f'/api/v1/tasks/{task_a.id}/complete/', {}, format='json')
        assert r.status_code == 200
        assert AuditEvent.objects.filter(event_type='task.completed').exists()

    def test_critical_delete_is_not_hard_delete(self, client_a, task_a):
        task_id = task_a.id
        r = client_a.delete(f'/api/v1/tasks/{task_id}/')
        assert r.status_code == 405
        task_a.__class__.objects.get(id=task_id)
