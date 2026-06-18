web: gunicorn metaguard_project.wsgi:application
worker: celery -A metaguard_project worker --loglevel=info
