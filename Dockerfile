FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Системные пакеты для сборки и подключения к PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала зависимости — для кеша
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем проект
COPY . /app/

# Стартовый скрипт
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
