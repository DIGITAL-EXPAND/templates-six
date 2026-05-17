from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from .models import ContractTemplate, ContractRecord, SignatureRecord
from .serializers import (
    ContractTemplateSerializer, ContractRecordSerializer, SignatureRecordSerializer,
)
from .services import (
    create_contract, issue_contract, record_signature, submit_for_review,
    cancel_contract, lock_final_contract,
)


class ContractTemplateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ContractTemplate.objects.all()
    serializer_class = ContractTemplateSerializer
    filterset_fields = ['contract_type', 'is_active']
    ordering = ['name']


class ContractRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ContractRecord.objects.select_related(
        'operating_context', 'template', 'signed_document',
    )
    serializer_class = ContractRecordSerializer
    filterset_fields = ['operating_context', 'contract_type', 'counterparty_type', 'status']
    search_fields = ['counterparty_name', 'notes']
    ordering_fields = ['created_at', 'issued_date', 'value']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        contract = create_contract(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = contract

    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        contract = self.get_object()
        updated = issue_contract(contract, request.user)
        return Response(ContractRecordSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='submit-for-review')
    def submit_for_review(self, request, pk=None):
        contract = self.get_object()
        review_type = request.data.get('review_type', '')
        updated = submit_for_review(contract, request.user, review_type)
        return Response(ContractRecordSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        updated = cancel_contract(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ContractRecordSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        updated = lock_final_contract(self.get_object(), request.user, request.data.get('comment', ''))
        return Response(ContractRecordSerializer(updated, context={'request': request}).data)


class SignatureRecordViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = SignatureRecord.objects.select_related('contract')
    serializer_class = SignatureRecordSerializer
    filterset_fields = ['contract', 'is_signed']
    ordering = ['signature_order', 'created_at']

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        sig = self.get_object()
        updated = record_signature(sig, request.user)
        return Response(SignatureRecordSerializer(updated, context={'request': request}).data)
