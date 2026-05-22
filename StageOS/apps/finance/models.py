import uuid
from django.db import models
from common.models import TenantOwnedModel


class GRAPAccountCategory(models.TextChoices):
    REVENUE_EXCHANGE = 'revenue_exchange', 'Revenue — Exchange (GRAP 9)'
    REVENUE_NON_EXCHANGE = 'revenue_non_exchange', 'Revenue — Non-Exchange (GRAP 23)'
    GRANTS_RECEIVED = 'grants_received', 'Grants & Subsidies Received'
    DONATIONS = 'donations', 'Donations & Bequests'
    EXPENSE_EMPLOYEE = 'expense_employee', 'Employee Costs'
    EXPENSE_GOODS_SERVICES = 'expense_goods', 'Goods & Services'
    EXPENSE_DEPRECIATION = 'expense_depreciation', 'Depreciation & Amortisation'
    EXPENSE_OTHER = 'expense_other', 'Other Expenses'
    ASSET_CURRENT = 'asset_current', 'Current Assets'
    ASSET_NON_CURRENT = 'asset_non_current', 'Non-Current Assets'
    LIABILITY_CURRENT = 'liability_current', 'Current Liabilities'
    LIABILITY_NON_CURRENT = 'liability_non_current', 'Non-Current Liabilities'
    EQUITY = 'equity', 'Net Assets / Equity'
    DEFERRED_INCOME = 'deferred_income', 'Deferred Income (Conditional Grants)'


class GLAccount(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=GRAPAccountCategory.choices)
    is_active = models.BooleanField(default=True)
    is_control_account = models.BooleanField(default=False)
    grap_standard = models.CharField(max_length=50, blank=True, help_text='e.g. GRAP 23, GRAP 9')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('organisation', 'account_code')]
        ordering = ['account_code']

    def __str__(self):
        return f'{self.account_code} — {self.name}'


class GrantRecognitionType(models.TextChoices):
    UNCONDITIONAL = 'unconditional', 'Unconditional — Recognised Immediately'
    CONDITIONAL = 'conditional', 'Conditional — Deferred Until Conditions Met'
    PERFORMANCE_BASED = 'performance_based', 'Performance-Based — Recognised on Achievement'


class GLJournalEntry(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255)
    entry_date = models.DateField()
    financial_year = models.CharField(max_length=9)
    period = models.PositiveSmallIntegerField(help_text='Accounting period 1-12')
    is_posted = models.BooleanField(default=False)
    posted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_journal_entries')
    posted_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=50, blank=True, help_text='e.g. grant_receipt, manual, payroll')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            count = GLJournalEntry.objects.filter(organisation=self.organisation).count() + 1
            self.reference = f'JE-{count:06d}'
        super().save(*args, **kwargs)


class GLJournalLine(TenantOwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal = models.ForeignKey(GLJournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(GLAccount, on_delete=models.PROTECT, related_name='journal_lines')
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['id']


class DeferredIncome(TenantOwnedModel):
    """Tracks conditional grant income deferred until conditions are met (GRAP 23)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grant_name = models.CharField(max_length=255)
    grantor = models.CharField(max_length=255)
    financial_year = models.CharField(max_length=9)
    recognition_type = models.CharField(max_length=20, choices=GrantRecognitionType.choices)
    total_grant_amount = models.DecimalField(max_digits=14, decimal_places=2)
    amount_recognised = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_deferred = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    conditions_description = models.TextField(blank=True)
    recognition_date = models.DateField(null=True, blank=True)
    is_fully_recognised = models.BooleanField(default=False)
    gl_account = models.ForeignKey(GLAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='deferred_income')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
