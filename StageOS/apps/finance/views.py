from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from common.views import TenantScopedMixin
from .models import GLAccount, GLJournalEntry, DeferredIncome
from .serializers import GLAccountSerializer, GLJournalEntrySerializer, DeferredIncomeSerializer


class GLAccountViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = GLAccount.objects.all()
    serializer_class = GLAccountSerializer

    @action(detail=False, methods=['get'])
    def trial_balance(self, request):
        """Returns trial balance — net debit/credit per account for a financial year."""
        fy = request.query_params.get('financial_year', '')
        accounts = self.get_queryset().filter(is_active=True)
        result = []
        for acc in accounts:
            lines = acc.journal_lines.filter(journal__is_posted=True)
            if fy:
                lines = lines.filter(journal__financial_year=fy)
            total_debit = sum(l.debit for l in lines)
            total_credit = sum(l.credit for l in lines)
            if total_debit or total_credit:
                result.append({
                    'account_code': acc.account_code,
                    'account_name': acc.name,
                    'category': acc.category,
                    'total_debit': float(total_debit),
                    'total_credit': float(total_credit),
                    'net': float(total_debit - total_credit),
                })
        return Response(result)


class GLJournalEntryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = GLJournalEntry.objects.prefetch_related('lines__account')
    serializer_class = GLJournalEntrySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        fy = self.request.query_params.get('financial_year')
        if fy:
            qs = qs.filter(financial_year=fy)
        return qs

    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        """Post a journal entry — validates it is balanced first."""
        entry = self.get_object()
        lines = entry.lines.all()
        total_debit = sum(l.debit for l in lines)
        total_credit = sum(l.credit for l in lines)
        if total_debit != total_credit:
            return Response({'error': f'Journal is not balanced. Debits: {total_debit}, Credits: {total_credit}'}, status=status.HTTP_400_BAD_REQUEST)
        entry.is_posted = True
        entry.posted_by = request.user
        entry.posted_at = timezone.now()
        entry.save()
        return Response(GLJournalEntrySerializer(entry).data)


class DeferredIncomeViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = DeferredIncome.objects.all()
    serializer_class = DeferredIncomeSerializer

    @action(detail=True, methods=['post'])
    def recognise(self, request, pk=None):
        """Partially or fully recognise deferred income."""
        record = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'amount is required'}, status=status.HTTP_400_BAD_REQUEST)
        amount = float(amount)
        remaining = float(record.total_grant_amount) - float(record.amount_recognised)
        if amount > remaining:
            return Response({'error': f'Cannot recognise more than remaining balance of {remaining}'}, status=status.HTTP_400_BAD_REQUEST)
        record.amount_recognised = float(record.amount_recognised) + amount
        record.amount_deferred = float(record.total_grant_amount) - float(record.amount_recognised)
        if record.amount_recognised >= record.total_grant_amount:
            record.is_fully_recognised = True
            record.recognition_date = timezone.now().date()
        record.save()
        return Response(DeferredIncomeSerializer(record).data)
