#!/usr/bin/env bash
set -e

echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT}..."   # Ожидаем базу данных
python - <<'PYCODE'
import os, time
import psycopg2
host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "postgres")
dbname = os.environ.get("DB_NAME", "tasktracker")

for i in range(30):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
        conn.close()
        print("Postgres is ready.")
        break
    except Exception as e:
        print(f"Postgres not ready yet ({e}). Retry {i+1}/30...")
        time.sleep(1)
else:
    raise SystemExit("Postgres not reachable after 30s.")
PYCODE

python manage.py migrate --noinput    # Миграции

python manage.py shell <<'PYCODE'     # Создание суперпользователя, если задан ENV и его ещё нет
import os
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL")
if u and p and e:
    if not User.objects.filter(username=u).exists():
        print(f"Creating superuser {u}...")
        User.objects.create_superuser(username=u, password=p, email=e)
    else:
        print(f"Superuser {u} already exists.")
else:
    print("Superuser env vars not provided; skipping creation.")
PYCODE

echo "Starting Django dev server at 0.0.0.0:8000 ..."   # Запуск сервера разработки (для прод — см. ниже раздел Production)
python manage.py runserver 0.0.0.0:8000
