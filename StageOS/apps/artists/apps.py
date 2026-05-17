from django.apps import AppConfig


class ArtistsConfig(AppConfig):
    name = 'apps.artists'
    label = 'artists'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Artists'
