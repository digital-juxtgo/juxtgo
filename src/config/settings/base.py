"""
Base settings for JuxtGo OS.

Contains environment‑agnostic configuration.
Secrets are loaded from environment variables using python-decouple.
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------------------------
# Core Django Settings
# ------------------------------------------------------------------------------
SECRET_KEY = config(
    "DJANGO_SECRET_KEY", default="django-insecure-fallback-key-for-dev-only"
)
DEBUG = False  # Overridden in development.py
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ------------------------------------------------------------------------------
# Authentication URLs – now namespaced under core:identity
# ------------------------------------------------------------------------------
LOGIN_URL = "core:identity:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "core:identity:login"

# ------------------------------------------------------------------------------
# Installed Apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third‑party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "whitenoise.runserver_nostatic",  # For WhiteNoise in development
    # dashboard
    "apps.dashboard",
    # JuxtGo OS internal apps
    "apps.core.identity",
    "apps.core.permissions",
    "apps.core.organizations",
    "apps.core.tenancy",
    "apps.core.crm",
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.active_menu_context",
            ],
        },
    },
]

# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL", default="postgres://user:password@localhost:5432/juxtgo"
        ),
        conn_max_age=600,
        ssl_require=config("DATABASE_SSL_REQUIRE", default=False, cast=bool),
    )
    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": config("POSTGRES_DB"),
    #     "USER": config("POSTGRES_USER"),
    #     "PASSWORD": config("POSTGRES_PASSWORD"),
    #     "HOST": config("POSTGRES_HOST", default="db"),
    #     "PORT": config("POSTGRES_PORT", default="5432"),
    #     "CONN_MAX_AGE": 600,
    #     "OPTIONS": {
    #         "sslmode": config("POSTGRES_SSLMODE", default="prefer"),
    #     },
    # }
}

# ------------------------------------------------------------------------------
# Custom User Model
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "identity.User"

# ------------------------------------------------------------------------------
# REST Framework & JWT
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ------------------------------------------------------------------------------
# Static & Media Files
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())

# ------------------------------------------------------------------------------
# Security Headers (Base: minimal; strengthen in production)
# ------------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = False  # Override in prod
SESSION_COOKIE_SECURE = False  # Override in prod
SECURE_SSL_REDIRECT = False  # Override in prod

# ------------------------------------------------------------------------------
# Email (console by default, override in prod)
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@juxtgo.local"

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
