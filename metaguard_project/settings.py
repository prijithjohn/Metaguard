import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",") if host.strip()]

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

DB_ENGINE = os.environ.get("DB_ENGINE", "django.db.backends.postgresql")
DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
    }
}

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES["default"]["NAME"] = BASE_DIR / "db.sqlite3"
else:
    DATABASES["default"].update({
        "NAME": os.environ.get("POSTGRES_DB", "metaguard"),
        "USER": os.environ.get("POSTGRES_USER", "metaguard_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "metaguard_pass"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    })

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

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "common" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Upload limits
# Maximum upload size in bytes (default 1 GB) - override with METAGUARD_MAX_UPLOAD_SIZE in env
# Chosen for production: supports large CSV/JSON datasets while maintaining safety
METAGUARD_MAX_UPLOAD_SIZE = int(os.environ.get("METAGUARD_MAX_UPLOAD_SIZE", 1073741824))  # 1 GB = 1024*1024*1024
# Memory threshold for streaming uploads to disk (25 MB): files larger than this are streamed to temporary files
# instead of held in RAM, preventing memory exhaustion during large file uploads
METAGUARD_MAX_MEMORY_UPLOAD_SIZE = int(os.environ.get("METAGUARD_MAX_MEMORY_UPLOAD_SIZE", 26214400))  # 25 MB = 25*1024*1024
METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE", 26214400))  # 25 MB = 25*1024*1024
METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get("METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS", 10000))

# Django limits for request/file uploads
# When files exceed FILE_UPLOAD_MAX_MEMORY_SIZE, Django streams them to FILE_UPLOAD_TEMP_DIR on disk
# This ensures large uploads don't exhaust server memory while processing
DATA_UPLOAD_MAX_MEMORY_SIZE = METAGUARD_MAX_MEMORY_UPLOAD_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = METAGUARD_FILE_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_TEMP_DIR = os.environ.get("FILE_UPLOAD_TEMP_DIR", None)  # Optional: specify temp directory for streaming large files
DATA_UPLOAD_MAX_NUMBER_FIELDS = METAGUARD_DATA_UPLOAD_MAX_NUMBER_FIELDS

# Authentication
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Cache
CACHES = {
    "default": {
        "BACKEND": os.environ.get(
            "DJANGO_CACHE_BACKEND",
            "django.core.cache.backends.locmem.LocMemCache",
        ),
        "LOCATION": "metaguard-cache",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery / Redis configuration (for async processing)
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_DEFAULT_QUEUE = os.environ.get("CELERY_TASK_DEFAULT_QUEUE", "default")
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", 60 * 60))
CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 60 * 60))
CELERY_BROKER_CONNECTION_TIMEOUT = int(os.environ.get("CELERY_BROKER_CONNECTION_TIMEOUT", 10))
CELERY_RESULT_EXPIRES = int(os.environ.get("CELERY_RESULT_EXPIRES", 60 * 60 * 24))
