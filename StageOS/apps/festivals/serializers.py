from rest_framework import serializers
from common.serializers import check_tenant_fk
from .models import Festival, FestivalVenue, FestivalPass, FestivalVenueSlot


class FestivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Festival
        fields = [
            'id', 'name', 'edition', 'status', 'start_date', 'end_date',
            'description', 'artistic_director', 'expected_attendance',
            'max_accreditation', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FestivalVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FestivalVenue
        fields = ['id', 'festival', 'venue', 'venue_code', 'is_primary', 'notes']
        read_only_fields = ['id']

    def validate_festival(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Festival')

    def validate_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Venue')


class FestivalPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = FestivalPass
        fields = [
            'id', 'festival', 'pass_type', 'holder_name', 'holder_email',
            'organisation_name', 'pass_number', 'valid_days', 'venue_access',
            'is_active', 'issued_date', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'pass_number', 'created_at']

    def validate_festival(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Festival')


class FestivalVenueSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FestivalVenueSlot
        fields = [
            'id', 'festival', 'festival_venue', 'operating_context',
            'slot_date', 'start_time', 'end_time', 'slot_label',
            'is_confirmed', 'notes',
        ]
        read_only_fields = ['id']

    def validate_festival(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Festival')

    def validate_festival_venue(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Festival venue')

    def validate_operating_context(self, value):
        if value is None:
            return value
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')
