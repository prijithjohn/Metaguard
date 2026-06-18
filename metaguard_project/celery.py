import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metaguard_project.settings")

app = Celery("metaguard_project")

# Use a string here so worker doesn't have to serialize the config object.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    return f"Debug: {self.request!r}"
