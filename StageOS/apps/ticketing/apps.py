from django.apps import AppConfig


class TicketingConfig(AppConfig):
    name = 'apps.ticketing'
    label = 'ticketing'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Ticketing'
