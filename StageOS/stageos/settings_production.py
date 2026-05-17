from django.core.exceptions import ImproperlyConfigured

from .settings import *

ENVIRONMENT = 'production'
DEBUG = env_bool('DEBUG', False)

if SECRET_KEY == 'django-insecure-dev-key-change-in-production':
    raise ImproperlyConfigured('SECRET_KEY must be set for production.')

SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
