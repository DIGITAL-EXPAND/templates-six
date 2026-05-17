from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from common.views import TenantScopedMixin
from .models import Document, EvidenceSubmission
from .serializers import DocumentSerializer, DocumentUploadSerializer, EvidenceSubmissionSerializer
from .services import (
    accept_evidence, record_document_download, store_uploaded_document,
    submit_evidence, set_document_lock, upload_document, reject_evidence,
)


class DocumentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Document.objects.select_related('operating_context', 'uploaded_by')
    serializer_class = DocumentSerializer
    filterset_fields = ['operating_context', 'document_type', 'is_locked']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        doc = upload_document(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = doc

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        input_serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        input_serializer.is_valid(raise_exception=True)
        vd = dict(input_serializer.validated_data)
        context_obj = vd.pop('operating_context')
        uploaded_file = vd.pop('file')
        doc = store_uploaded_document(
            context=context_obj,
            user=request.user,
            uploaded_file=uploaded_file,
            data=vd,
        )
        return Response(DocumentSerializer(doc, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        doc = self.get_object()
        if not doc.file:
            return Response({'detail': 'No stored file is available for this document.'}, status=status.HTTP_404_NOT_FOUND)
        record_document_download(doc, request.user)
        return FileResponse(
            doc.file.open('rb'),
            as_attachment=True,
            filename=doc.file_name,
            content_type=doc.mime_type or 'application/octet-stream',
        )

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        doc = self.get_object()
        updated = set_document_lock(doc, request.user, True, request.data.get('comment', ''))
        return Response(DocumentSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        doc = self.get_object()
        updated = set_document_lock(doc, request.user, False, request.data.get('comment', ''))
        return Response(DocumentSerializer(updated, context={'request': request}).data)


class EvidenceSubmissionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = EvidenceSubmission.objects.select_related(
        'operating_context', 'task', 'document', 'submitted_by', 'accepted_by',
    )
    serializer_class = EvidenceSubmissionSerializer
    filterset_fields = ['operating_context', 'task', 'accepted']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        vd = dict(serializer.validated_data)
        context_obj = vd.pop('operating_context')
        submission = submit_evidence(context=context_obj, user=self.request.user, data=vd)
        serializer.instance = submission

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        submission = self.get_object()
        updated = accept_evidence(submission, request.user)
        return Response(EvidenceSubmissionSerializer(updated, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        submission = self.get_object()
        updated = reject_evidence(submission, request.user, request.data.get('reason', ''))
        return Response(EvidenceSubmissionSerializer(updated, context={'request': request}).data)
