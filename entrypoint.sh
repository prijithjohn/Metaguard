#!/bin/sh
set -eu

wait_for_postgres() {
    if [ "${DB_ENGINE:-django.db.backends.postgresql}" = "django.db.backends.sqlite3" ]; then
        echo "Using SQLite; skipping database wait."
        return 0
    fi

    host="${POSTGRES_HOST:-db}"
    port="${POSTGRES_PORT:-5432}"
    echo "Waiting for PostgreSQL at ${host}:${port}..."

    for _ in $(seq 1 60); do
        python - <<'PY'
import os
import socket
import sys

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(1)
    try:
        sock.connect((host, port))
    except OSError:
        sys.exit(1)
    sys.exit(0)
PY
        if [ $? -eq 0 ]; then
            echo "PostgreSQL is available."
            return 0
        fi
        sleep 2
    done

    echo "PostgreSQL did not become ready in time." >&2
    exit 1
}

wait_for_postgres

echo "Running database migrations..."
python manage.py migrate --noinput

if [ "${1:-}" = "gunicorn" ]; then
    mkdir -p staticfiles
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Starting ${1:-web}..."
exec "$@"