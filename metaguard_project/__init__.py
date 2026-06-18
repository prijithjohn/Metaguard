# Celery not currently configured
# from .celery import app as celery_app
# __all__ = ("celery_app",)
import warnings

try:
	from .celery import app as celery_app
except ModuleNotFoundError:
	warnings.warn('Celery is not installed or metaguard_project.celery is missing; continuing without celery_app')
	celery_app = None

__all__ = ("celery_app",)
