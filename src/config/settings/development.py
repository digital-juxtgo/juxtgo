from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable password validators for convenience
AUTH_PASSWORD_VALIDATORS = []

# Use console email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable security redirects for local HTTP
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Verbose logging in dev
LOGGING["loggers"] = {
    "django": {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": False,
    },
    "apps.core": {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    },
}