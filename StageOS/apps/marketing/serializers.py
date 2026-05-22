from rest_framework import serializers
from common.serializers import (
    check_tenant_fk, validate_unique_context, ProtectedFieldsMixin, require_non_negative,
)
from .models import Campaign, CampaignDeliverable, SocialPost, AudienceReport, MediaContact, NewsletterCampaign, CIComplianceCheck


class CampaignSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = Campaign
        fields = [
            'id', 'operating_context', 'campaign_level', 'budget',
            'status', 'owner', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)

    def validate_owner(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Owner')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, ['budget'])
        return attrs


class CampaignDeliverableSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)
    class Meta:
        model = CampaignDeliverable
        fields = [
            'id', 'campaign', 'deliverable_type', 'title', 'owner_name',
            'due_date', 'status', 'completed_at', 'evidence_document',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'completed_at', 'created_at', 'updated_at']

    def validate_campaign(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Campaign')

    def validate_evidence_document(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Evidence document')


class SocialPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPost
        fields = [
            'id', 'campaign', 'platform', 'content', 'media_url', 'status',
            'scheduled_at', 'published_at', 'reach', 'impressions', 'engagements',
            'clicks', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'published_at', 'created_at', 'updated_at']

    def validate_campaign(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Campaign')


class AudienceReportSerializer(serializers.ModelSerializer):
    occupancy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = AudienceReport
        fields = [
            'id', 'operating_context', 'total_attendance', 'capacity_total',
            'comps_issued', 'school_groups', 'average_ticket_price', 'gross_revenue',
            'demographics_notes', 'feedback_summary', 'average_rating',
            'is_finalised', 'occupancy_rate', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'occupancy_rate', 'created_at', 'updated_at']

    def validate_operating_context(self, value):
        check_tenant_fk(value, self.context.get('request'), 'Operating context')
        return validate_unique_context(self, value)


class MediaContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaContact
        fields = [
            'id', 'name', 'outlet', 'role', 'email', 'phone',
            'coverage_type', 'is_active', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NewsletterCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'subject', 'status', 'audience_description', 'body_text',
            'scheduled_send_date', 'sent_date', 'recipient_count', 'open_rate',
            'click_rate', 'linked_productions', 'prepared_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_prepared_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Prepared by')


class CIComplianceCheckSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = ('status',)

    class Meta:
        model = CIComplianceCheck
        fields = [
            'id', 'operating_context', 'material_type', 'status',
            'submitted_by', 'reviewed_by', 'submission_date', 'review_date',
            'feedback', 'version', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate_submitted_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Submitted by')

    def validate_reviewed_by(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Reviewed by')
