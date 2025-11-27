#!/bin/bash
set -e

echo "=========================================="
echo "Django Sales Application - Starting"
echo "=========================================="

# Ожидаем, пока база данных будет доступна
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Database is ready!"

# Выполняем миграции
echo "Running database migrations..."
python manage.py migrate --noinput

# Собираем статические файлы
echo "Collecting static files..."
# Убедимся, что директория для статических файлов существует и доступна
mkdir -p "$STATIC_ROOT"
chmod -R 777 "$STATIC_ROOT" || true
python manage.py collectstatic --noinput

# Создаем суперпользователя, если его нет (опционально)
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "Creating superuser..."
  python manage.py shell <<END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created successfully")
else:
    print("Superuser 'admin' already exists")
END
fi

echo "=========================================="
echo "Starting application..."
echo "=========================================="

# Передаем управление основной команде
exec "$@"
