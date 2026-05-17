from rest_framework import serializers
from django.conf import settings
from common.serializers import check_tenant_fk, ProtectedFieldsMixin
from .models import Document, EvidenceSubmission


class DocumentSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('is_locked', 'storage_ref', 'file')
    class Meta:
        model = Document
        fields = [
            'id', 'operating_context', 'title', 'document_type', 'file_name',
            'file_size', 'mime_type', 'storage_ref', 'file', 'version', 'uploaded_by',
            'is_locked', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'is_locked', 'storage_ref', 'file', 'created_at', 'updated_at',
        ]

    def validate_file_size(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('File size cannot be negative.')
        return value

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')


class DocumentUploadSerializer(serializers.Serializer):
    operating_context = serializers.PrimaryKeyRelatedField(queryset=[])
    title = serializers.CharField(max_length=255)
    document_type = serializers.CharField(max_length=30)
    file = serializers.FileField()
    version = serializers.IntegerField(required=False, min_value=1, default=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.contexts.models import OperatingContext
            self.fields['operating_context'].queryset = OperatingContext.objects.filter(
                organisation_id=request.user.organisation_id,
            )

    def validate_file(self, value):
        max_bytes = getattr(settings, 'STAGEOS_MAX_UPLOAD_BYTES', 25 * 1024 * 1024)
        if value.size > max_bytes:
            raise serializers.ValidationError(f'File exceeds the configured {max_bytes} byte limit.')
        content_type = getattr(value, 'content_type', '') or ''
        allowed = set(getattr(settings, 'STAGEOS_ALLOWED_UPLOAD_MIME_TYPES', []))
        if allowed and content_type not in allowed:
            raise serializers.ValidationError('File type is not allowed.')
        return value


class EvidenceSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceSubmission
        fields = [
            'id', 'operating_context', 'task', 'document', 'submitted_by',
            'submission_note', 'accepted', 'accepted_by', 'accepted_at',
            'rejected', 'rejected_by', 'rejected_at', 'rejection_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'submitted_by', 'accepted', 'accepted_by', 'accepted_at',
            'rejected', 'rejected_by', 'rejected_at', 'rejection_reason',
            'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_task(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Task')

    def validate_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Document')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        context = attrs.get('operating_context', getattr(self.instance, 'operating_context', None))
        task = attrs.get('task', getattr(self.instance, 'task', None))
        document = attrs.get('document', getattr(self.instance, 'document', None))
        if context and task and task.operating_context_id != context.id:
            raise serializers.ValidationError('Task must belong to the selected operating context.')
        if context and document and document.operating_context_id != context.id:
            raise serializers.ValidationError('Document must belong to the selected operating context.')
        return attrs
