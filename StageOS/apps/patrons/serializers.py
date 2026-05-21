from rest_framework import serializers
from .models import Patron, PatronAttendance, PatronCommunication


class PatronAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatronAttendance
        fields = ['id', 'patron', 'operating_context', 'performance', 'attendance_date',
                  'tickets_count', 'amount_paid', 'channel', 'is_comp',
                  'feedback_rating', 'feedback_comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatronSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    recent_attendances = PatronAttendanceSerializer(
        source='attendances', many=True, read_only=True
    )

    class Meta:
        model = Patron
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
                  'segment', 'source', 'postal_code', 'city', 'province',
                  'marketing_opt_in', 'popia_consent_given', 'popia_consent_date',
                  'is_active', 'total_bookings', 'total_spend',
                  'first_visit_date', 'last_visit_date', 'notes',
                  'created_at', 'updated_at', 'recent_attendances']
        read_only_fields = ['id', 'total_bookings', 'total_spend',
                            'first_visit_date', 'last_visit_date', 'created_at', 'updated_at']


class PatronCommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatronCommunication
        fields = ['id', 'patron', 'subject', 'body', 'channel', 'sent_at',
                  'sent_by', 'operating_context', 'created_at']
        read_only_fields = ['id', 'created_at']


# ── Donors / Donations ────────────────────────────────────────────────────────

from rest_framework import serializers as _s
from .models import Donor, Donation  # noqa: E402


class DonationSerializer(_s.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'operating_context', 'financial_year', 'status',
            'amount_pledged', 'amount_received', 'pledge_date', 'received_date',
            'section_18a_issued', 'section_18a_date', 'purpose', 'conditions',
            'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class DonorSerializer(_s.ModelSerializer):
    class Meta:
        model = Donor
        fields = [
            'id', 'name', 'category', 'contact_person', 'email', 'phone',
            'address', 'tax_exempt_number', 'is_section_18a', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
