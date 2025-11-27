# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем метаданные
LABEL maintainer="sales-app@example.com"
LABEL description="Django Sales Application"

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статические файлы (будут собраны при запуске entrypoint)
# RUN python manage.py collectstatic --noinput

# Создаем пользователя для запуска приложения (безопасность)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# Экспонируем порт
EXPOSE 8000

# Копируем и запускаем entrypoint скрипт (делаем это как root до переключения на non-root пользователя)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ENTRYPOINT stays running as root so entrypoint can prepare volumes
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "sales_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
