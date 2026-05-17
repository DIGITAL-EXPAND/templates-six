from django.db import models


class ContextType(models.TextChoices):
    PRODUCTION = 'production', 'Production'
    VENUE_RENTAL = 'venue_rental', 'Venue Rental'
    CO_PRODUCTION = 'co_production', 'Co-Production'
    YOUTH_PROJECT = 'youth_project', 'Youth Project'
    FESTIVAL = 'festival', 'Festival'
    WORKSHOP_SERIES = 'workshop_series', 'Workshop Series'
    CIVIC_EVENT = 'civic_event', 'Civic Event'
    GOVERNANCE_ITEM = 'governance_item', 'Governance Item'


class ContextStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PRODUCTION = 'in_production', 'In Production'
    IN_DELIVERY = 'in_delivery', 'In Delivery'
    COMPLETED = 'completed', 'Completed'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'
    REJECTED = 'rejected', 'Rejected'


class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class RiskLevel(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'
