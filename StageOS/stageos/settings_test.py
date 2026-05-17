from .settings import *

ENVIRONMENT = 'test'
DEBUG = env_bool('DEBUG', False)
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
