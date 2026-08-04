import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8001,http://localhost:8001",
    ).split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "common",
    "datasets",
    "metadata",
    "quality",
    "governance",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.GlobalExceptionMiddleware",
]

ROOT_URLCONF = "metaguard_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "common" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "metaguard_project.wsgi.application"

DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.postgresql")
DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
    }
}

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES["default"]["NAME"] = BASE_DIR / "db.sqlite3"
else:
    DATABASES["default"].update(
        {
            "NAME": os.getenv("POSTGRES_DB", "metaguard"),
            "USER": os.getenv("POSTGRES_USER", "metaguard_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "metaguard_pass"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    )

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = os.getenv("USE_X_FORWARDED_HOST", "False") == "True"
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = "DENY"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "common" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Upload limits
# Maximum upload size in bytes (default 1 GB) - override with METAGUARD_MAX_UPLOAD_SIZE in env
# Chosen for production: supports large CSV/JSON datasets while maintaining safety
METAGUARD_MAX_UPLOAD_SIZE = int(
    os.getenv("METAGUARD_MAX_UPLOAD_SIZE", 1073741824)
)  # 1 GB = 1024*1024*1024
# Memory threshold for streaming uploads to disk (25 MB): files larger than this
# are streamed to temporary files instead of held in RAM, preventing memory
# exhaustion during large file uploads.
METAGUARD_MAX_MEMORY_UPLOAD_SIZE = int(
    os.getenv("METAGUARD_MAX_MEMORY_UPLOAD_SIZE", 26214400)
)  # 25 MB = 25*1024*1024
METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE = int(
    os.getenv("METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE", 26214400)
)  # 25 MB = 25*1024*1024
METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS = int(
    os.getenv("METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS", 10000)
)

# Django limits for request/file uploads
# When files exceed FILE_UPLOAD_MAX_MEMORY_SIZE, Django streams them to FILE_UPLOAD_TEMP_DIR on disk
# This ensures large uploads don't exhaust server memory while processing
DATA_UPLOAD_MAX_MEMORY_SIZE = METAGUARD_MAX_MEMORY_UPLOAD_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_TEMP_DIR = os.getenv(
    "FILE_UPLOAD_TEMP_DIR", None
)  # Optional: specify temp directory for streaming large files
DATA_UPLOAD_MAX_NUMBER_FIELDS = METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS

# Authentication
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Cache
CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "DJANGO_CACHE_BACKEND",
            "django.core.cache.backends.locmem.LocMemCache",
        ),
        "LOCATION": "metaguard-cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if DEBUG else "WARNING",
    },
}

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
