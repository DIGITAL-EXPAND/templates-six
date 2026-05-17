from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    name = 'apps.suppliers'
    label = 'suppliers'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Suppliers'
