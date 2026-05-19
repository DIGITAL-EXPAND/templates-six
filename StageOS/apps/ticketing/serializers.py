from rest_framework import serializers
from common.serializers import check_tenant_fk, ProtectedFieldsMixin, require_non_negative
from .models import TicketingSetup, SalesImport, PriceCategory, Booking, Ticket, TillReconciliation


class TicketingSetupSerializer(ProtectedFieldsMixin, serializers.ModelSerializer):
    protected_fields = (
        'setup_status', 'sales_imported', 'tickets_sold',
        'settlement_status', 'settlement_amount',
    )
    class Meta:
        model = TicketingSetup
        fields = [
            'id', 'operating_context', 'provider', 'booking_link',
            'pricing_description', 'comps_allocated', 'comps_used',
            'setup_status', 'sales_imported', 'tickets_sold', 'tickets_available',
            'settlement_status', 'settlement_amount', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'setup_status', 'sales_imported', 'tickets_sold',
            'settlement_status', 'settlement_amount', 'created_at', 'updated_at',
        ]

    def validate_operating_context(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Operating context')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        require_non_negative(attrs, [
            'comps_allocated', 'comps_used', 'tickets_sold',
            'tickets_available', 'settlement_amount',
        ])
        return attrs


class SalesImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesImport
        fields = [
            'id', 'ticketing_setup', 'import_date', 'tickets_sold',
            'revenue', 'imported_by', 'source_file', 'notes',
        ]
        read_only_fields = ['id', 'import_date', 'imported_by']

    def validate_ticketing_setup(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Ticketing setup')

    def validate_source_file(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Source file')


class ImportSalesSerializer(serializers.Serializer):
    tickets_sold = serializers.IntegerField(min_value=0)
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, default='', allow_blank=True)
    source_file = serializers.UUIDField(required=False, allow_null=True, default=None)

    def validate_revenue(self, value):
        if value < 0:
            raise serializers.ValidationError('Value cannot be negative.')
        return value


class SettleSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('Value cannot be negative.')
        return value


class PriceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceCategory
        fields = ['id', 'ticketing_setup', 'name', 'price', 'is_comp', 'sort_order']
        read_only_fields = ['id']

    def validate_ticketing_setup(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Ticketing setup')


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'booking', 'price_category', 'seat_reference',
            'status', 'amount', 'checked_in', 'checked_in_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_booking(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Booking')

    def validate_price_category(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Price category')


class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'ticketing_setup', 'performance', 'booking_reference',
            'patron_name', 'patron_email', 'patron_phone', 'channel',
            'total_amount', 'is_group_booking', 'group_name', 'notes',
            'booked_at', 'updated_at', 'tickets',
        ]
        read_only_fields = ['id', 'booked_at', 'updated_at']

    def validate_ticketing_setup(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Ticketing setup')

    def validate_performance(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Performance')


class TillReconciliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TillReconciliation
        fields = [
            'id', 'ticketing_setup', 'performance', 'recon_date',
            'cash_counted', 'card_total', 'system_total', 'variance',
            'variance_explained', 'signed_off_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_ticketing_setup(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Ticketing setup')

    def validate_performance(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Performance')

    def validate_signed_off_by(self, value):
        return check_tenant_fk(value, self.context.get('request'), 'Signed off by')
