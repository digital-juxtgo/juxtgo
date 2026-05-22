from .base import *

DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# ------------------------------------------------------------------------------
# Security Hardening (HTTPS required)
# ------------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ------------------------------------------------------------------------------
# Email (SMTP)
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# ------------------------------------------------------------------------------
# Database – require SSL if configured
# ------------------------------------------------------------------------------
DATABASES["default"]["OPTIONS"]["sslmode"] = config("POSTGRES_SSLMODE", default="require")

# ------------------------------------------------------------------------------
# Logging – more structured in production
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps.core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ------------------------------------------------------------------------------
# Static files – may use CDN in addition to WhiteNoise
# ------------------------------------------------------------------------------
# STATIC_URL = "https://cdn.example.com/static/"