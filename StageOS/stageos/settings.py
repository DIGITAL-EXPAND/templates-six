import os
from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

ENVIRONMENT = os.environ.get('STAGEOS_ENV', os.environ.get('ENVIRONMENT', 'local')).lower()

def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if ENVIRONMENT in {'production', 'prod', 'staging'}:
        raise ImproperlyConfigured('SECRET_KEY must be set outside local/test environments.')
    SECRET_KEY = 'django-insecure-dev-key-change-in-production'

DEBUG = env_bool('DEBUG', ENVIRONMENT in {'local', 'test'})

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
    # Core
    'common',
    # Active apps
    'apps.organisations.apps.OrganisationsConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.audit.apps.AuditConfig',
    # Placeholder apps (future sprints)
    'apps.structure.apps.StructureConfig',
    'apps.contexts.apps.ContextsConfig',
    'apps.programming.apps.ProgrammingConfig',
    'apps.marketing.apps.MarketingConfig',
    'apps.technical.apps.TechnicalConfig',
    'apps.operations.apps.OperationsConfig',
    'apps.contracts.apps.ContractsConfig',
    'apps.suppliers.apps.SuppliersConfig',
    'apps.artists.apps.ArtistsConfig',
    'apps.ticketing.apps.TicketingConfig',
    'apps.patrons.apps.PatronsConfig',
    'apps.youth.apps.YouthConfig',
    'apps.governance.apps.GovernanceConfig',
    'apps.workflows.apps.WorkflowsConfig',
    'apps.approvals.apps.ApprovalsConfig',
    'apps.tasks.apps.TasksConfig',
    'apps.documents.apps.DocumentsConfig',
    'apps.integrations.apps.IntegrationsConfig',
    'apps.hospitality.apps.HospitalityConfig',
    'apps.reports.apps.ReportsConfig',
    'apps.finance.apps.FinanceConfig',  # GRAP-compliant GL
    'apps.festivals.apps.FestivalsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.middleware.RLSMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stageos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stageos.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloud file storage (S3 or Azure, configured via env)
DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'af-south-1')
AWS_S3_FILE_OVERWRITE = env_bool('AWS_S3_FILE_OVERWRITE', False)
AWS_DEFAULT_ACL = os.environ.get('AWS_DEFAULT_ACL', 'private')
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', '')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', '')
AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', '')
SIGNED_URL_EXPIRY_SECONDS = int(os.environ.get('SIGNED_URL_EXPIRY_SECONDS', '300'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_MINUTES', '15'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.environ.get('JWT_REFRESH_TOKEN_DAYS', '1'))
    ),
    'ROTATE_REFRESH_TOKENS': env_bool('JWT_ROTATE_REFRESH_TOKENS', False),
    'BLACKLIST_AFTER_ROTATION': env_bool('JWT_BLACKLIST_AFTER_ROTATION', False),
}

DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024))
STAGEOS_MAX_UPLOAD_BYTES = int(os.environ.get('STAGEOS_MAX_UPLOAD_BYTES', 20 * 1024 * 1024))
STAGEOS_ALLOWED_UPLOAD_MIME_TYPES = env_list(
    'STAGEOS_ALLOWED_UPLOAD_MIME_TYPES',
    'application/pdf,image/jpeg,image/png,image/webp,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
)

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
STAGEOS_FRONTEND_ORIGINS = env_list('STAGEOS_FRONTEND_ORIGINS')
CORS_ALLOWED_ORIGINS = STAGEOS_FRONTEND_ORIGINS

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'DENY')

if ENVIRONMENT in {'production', 'prod', 'staging'}:
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
    CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', False)
else:
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
    SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', False)
    CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', False)
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 0))

SPECTACULAR_SETTINGS = {
    'TITLE': 'StageOS API',
    'DESCRIPTION': 'Theatre governance and operations platform.',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Email
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'StageOS <noreply@stageos.local>')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'http://localhost:3000')
