from django.apps import AppConfig


class TechnicalConfig(AppConfig):
    name = 'apps.technical'
    label = 'technical'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Technical'
