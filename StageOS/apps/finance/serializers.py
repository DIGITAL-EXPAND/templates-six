from rest_framework import serializers
from .models import GLAccount, GLJournalEntry, GLJournalLine, DeferredIncome


class GLAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GLAccount
        fields = '__all__'
        read_only_fields = ['id', 'organisation', 'created_at']


class GLJournalLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = GLJournalLine
        fields = '__all__'
        read_only_fields = ['id', 'organisation']


class GLJournalEntrySerializer(serializers.ModelSerializer):
    lines = GLJournalLineSerializer(many=True, read_only=True)
    total_debits = serializers.SerializerMethodField()
    total_credits = serializers.SerializerMethodField()
    is_balanced = serializers.SerializerMethodField()

    class Meta:
        model = GLJournalEntry
        fields = '__all__'
        read_only_fields = ['id', 'organisation', 'reference', 'created_at']

    def get_total_debits(self, obj):
        return float(sum(l.debit for l in obj.lines.all()))

    def get_total_credits(self, obj):
        return float(sum(l.credit for l in obj.lines.all()))

    def get_is_balanced(self, obj):
        debits = sum(l.debit for l in obj.lines.all())
        credits = sum(l.credit for l in obj.lines.all())
        return debits == credits


class DeferredIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeferredIncome
        fields = '__all__'
        read_only_fields = ['id', 'organisation', 'created_at', 'updated_at']
