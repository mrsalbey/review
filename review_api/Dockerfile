FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

RUN mkdir /app
WORKDIR /app

# Установка системных зависимостей с очисткой кэша
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Копируем и устанавливаем зависимости
COPY review_api/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

# Копируем весь проект
COPY review_api/ .

# Создаем недостающие __init__.py файлы
#RUN find . -type d -name "__pycache__" -prune -o -type d -exec touch {}/__init__.py \;

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Выполняем миграции (если БД доступна) или оставляем для runtime
# RUN python manage.py migrate --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "settings.wsgi:application"]