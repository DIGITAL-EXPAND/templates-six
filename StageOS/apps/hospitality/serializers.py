from rest_framework import serializers
from .models import HospitalityRequest, HospitalityNote


class HospitalityNoteSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = HospitalityNote
        fields = [
            'id', 'hospitality_request', 'note_text', 'note_type',
            'created_by', 'created_by_email', 'created_by_name', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.email
        return ''


class HospitalityRequestSerializer(serializers.ModelSerializer):
    notes = HospitalityNoteSerializer(many=True, read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    operating_context_title = serializers.CharField(
        source='operating_context.title', read_only=True, default='',
    )

    class Meta:
        model = HospitalityRequest
        fields = [
            'id', 'operating_context', 'operating_context_title',
            'request_type', 'event_date', 'guest_count',
            'special_requirements', 'dietary_restrictions',
            'contact_name', 'contact_phone', 'status',
            'assigned_to', 'assigned_to_name', 'notes_text', 'notes',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.full_name or obj.assigned_to.email
        return ''
