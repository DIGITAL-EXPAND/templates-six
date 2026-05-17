from .settings import *

ENVIRONMENT = 'staging'
DEBUG = env_bool('DEBUG', False)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
