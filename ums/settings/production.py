from .base import *  # noqa F401
from .base import get_env_variable

DEBUG = False
ALLOWED_HOSTS = get_env_variable("DJANGO_ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": get_env_variable("DJANGO_DB_ENGINE", "django.db.backends.mysql"),
        "NAME": get_env_variable("DJANGO_DB_NAME"),
        "USER": get_env_variable("DJANGO_DB_USER"),
        "PASSWORD": get_env_variable("DJANGO_DB_PASSWORD"),
        "HOST": get_env_variable("DJANGO_DB_HOST"),
        "PORT": get_env_variable("DJANGO_DB_PORT", "3306"),
    }
}

# Security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
