from django.apps import AppConfig


class MarketingConfig(AppConfig):
    name = 'apps.marketing'
    label = 'marketing'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Marketing'
