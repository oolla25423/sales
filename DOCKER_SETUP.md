# Docker Setup - Подробное руководство

## Содержание

1. [Требования](#требования)
2. [Быстрый старт](#быстрый-старт)
3. [Архитектура](#архитектура)
4. [Детальное описание файлов](#детальное-описание-файлов)
5. [Развертывание](#развертывание)
6. [Мониторинг и отладка](#мониторинг-и-отладка)
7. [Очистка](#очистка)

## Требования

- Docker Engine 20.10 или выше
- Docker Compose 1.29 или выше
- 4GB RAM (минимум для PostgreSQL + Django)
- 2GB свободного места на диске

### Проверка установки

```bash
docker --version
docker-compose --version
```

## Быстрый старт

### 1. Подготовка окружения

```bash
cd /path/to/sales
cp .env.example .env
```

### 2. Для разработки (SQLite)

```bash
# Просто запустить с SQLite (без PostgreSQL)
docker build -t sales-app .
docker run -p 8000:8000 -v $(pwd):/app sales-app
```

**Windows PowerShell:**
```powershell
docker run -p 8000:8000 -v ${PWD}:/app sales-app
```

Приложение: http://localhost:8000/

### 3. Для разработки/production (PostgreSQL)

```bash
# Отредактируйте .env если нужно
nano .env

# Запустите all-in-one stack
docker-compose up -d --build

# Проверьте статус
docker-compose ps

# Логи
docker-compose logs -f web
```

Приложение: http://localhost:8000/

### 4. Для production с Nginx

```bash
docker-compose --profile production up -d --build
```

Приложение: http://localhost/

## Архитектура

### Development Setup

```
┌─────────────────────────────────────────┐
│        Docker Compose Network           │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐      ┌─────────────┐ │
│  │   Django     │──────│ PostgreSQL  │ │
│  │   Web App    │      │   15-alpine │ │
│  │  :8000       │      │   :5432     │ │
│  └──────────────┘      └─────────────┘ │
│         ↓                       ↓        │
│    Mount: /app         pgdata volume    │
│                                         │
└─────────────────────────────────────────┘
```

### Production Setup

```
┌──────────────────────────────────────────────────┐
│        Docker Compose Network (Production)       │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌───────────┐    ┌──────────────┐  ┌─────────┐│
│  │   Nginx   │    │   Django     │  │ Postgres││
│  │   :80     │───▶│   Web App    │──│  DB     ││
│  └───────────┘    │   :8000      │  └─────────┘│
│         ▲         └──────────────┘              │
│         │                                       │
│    :80 (внешний)                                │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Детальное описание файлов

### Dockerfile

**Назначение:** Образ для Django приложения

**Основные компоненты:**
- Base image: Python 3.11-slim (минимальный размер)
- Системные зависимости: gcc, postgresql-client
- Рабочая директория: /app
- Non-root пользователь: appuser (безопасность)
- Точка входа: entrypoint.sh

**Оптимизация:**
- Multi-stage подход (если бы компилировалось)
- Использование slim образа вместо полного
- Кэширование слоев (requirements скопирован отдельно)

### docker-compose.yml

**Структура:**

1. **Service: db**
   - PostgreSQL 15-alpine
   - Volume для персистентности: postgres_data
   - Health check для готовности
   - Network: sales_network

2. **Service: web**
   - Django приложение
   - Зависит от db (wait for health check)
   - Volumes:
     - Код приложения: /app
     - Статика: /app/staticfiles
     - Медиа: /app/uploads
   - Переменные из .env

3. **Service: nginx** (production profile)
   - Обратный прокси
   - Serve статики
   - Port 80

4. **Volumes:**
   - postgres_data: для БД
   - static_volume: для статических файлов
   - media_volume: для загруженных файлов

5. **Networks:**
   - sales_network (custom bridge)

### .dockerignore

**Исключает:**
- .git и git файлы
- Python кэш и virtual environments
- IDE конфигурации
- .env (но не .env.example)
- Тестовые данные
- Документация

**Результат:** Меньший размер образа (~200MB вместо 500MB+)

### .env.example

**Назначение:** Шаблон переменных для разработки

**Содержит:**
- Django settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- Database config (engine, name, credentials, host)
- Static/Media paths
- Security settings

### entrypoint.sh

**Выполняемые действия при старте контейнера:**

1. Ожидание доступности БД
2. Запуск миграций (`migrate`)
3. Сбор статических файлов (`collectstatic`)
4. Опциональное создание суперпользователя
5. Передача управления основной команде (gunicorn)

### nginx.conf

**Конфигурация:**
- Listen на port 80
- Upstream к Django приложению на :8000
- Serve статики из /app/staticfiles
- Serve загруженных файлов из /app/uploads
- Кэширование (30 дней для статики, 7 для медиа)
- Proxy headers для X-Real-IP, X-Forwarded-For

### settings.py (обновленный)

**Изменения:**
- Импорт python-dotenv для загрузки .env
- Динамическое определение ALLOWED_HOSTS
- Поддержка как PostgreSQL, так и SQLite
- Переменные для STATIC_ROOT и MEDIA_ROOT
- Connection pooling для PostgreSQL

## Развертывание

### Development Build

```bash
# Сборка образа
docker build -t sales-app:latest .

# Запуск контейнера (SQLite)
docker run -d \
  --name sales_dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e DEBUG=True \
  -e DJANGO_SECRET_KEY=dev-key \
  sales-app

# Доступ
open http://localhost:8000
```

### Docker Compose - Development

```bash
# Up with build
docker-compose up --build

# Up in background
docker-compose up -d --build

# Logfiles
docker-compose logs -f web

# Status
docker-compose ps

# Down (keep volumes)
docker-compose down

# Down (remove everything)
docker-compose down -v
```

### Docker Compose - Production

```bash
# Обновите .env для production
# - DEBUG=False
# - DJANGO_SECRET_KEY=<new-random-key>
# - DB_PASSWORD=<strong-password>
# - ALLOWED_HOSTS=yourdomain.com

# Запустите с Nginx
docker-compose --profile production up -d --build

# Проверьте
docker-compose ps
curl http://localhost
```

### Push на Docker Registry

```bash
# Login
docker login

# Tag
docker tag sales-app:latest myregistry/sales-app:v1.0

# Push
docker push myregistry/sales-app:v1.0

# Deploy на удаленный сервер
docker pull myregistry/sales-app:v1.0
docker run -d myregistry/sales-app:v1.0
```

## Мониторинг и отладка

### Просмотр логов

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web

# Follow logs
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail 100 web

# Since specific time
docker-compose logs --since 10m web
```

### Доступ к контейнерам

```bash
# Shell в web контейнере
docker-compose exec web bash

# Django shell
docker-compose exec web python manage.py shell

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web python manage.py test

# DB shell (PostgreSQL)
docker-compose exec db psql -U postgres -d sales_db
```

### Проверка статуса

```bash
# Контейнеры
docker-compose ps

# Сетевые подключения
docker network ls
docker network inspect sales_sales_network

# Volumes
docker volume ls
docker volume inspect sales_postgres_data

# Использование ресурсов
docker stats

# Логи системы
docker-compose logs --tail 50
```

### Типичные проблемы

**Problem: Контейнер зависает при старте**
```bash
# Решение: Проверьте логи
docker-compose logs web

# Могут быть проблемы с миграциями
docker-compose exec web python manage.py migrate --verbose

# Проверьте БД
docker-compose exec db psql -U postgres -d sales_db -c "\dt"
```

**Problem: Не подключается к БД**
```bash
# Проверьте health check
docker-compose exec db pg_isready -U postgres -d sales_db

# Проверьте переменные окружения
docker-compose config | grep -E "DB_|POSTGRES_"

# Проверьте network connectivity
docker-compose exec web nc -vz db 5432
```

**Problem: Статические файлы не работают**
```bash
# Проверьте volume
docker volume ls | grep static

# Пересобрать статику
docker-compose exec web python manage.py collectstatic --noinput

# Проверьте nginx config
docker-compose exec nginx cat /etc/nginx/nginx.conf | grep -A 5 "static"

# Проверьте права доступа
docker-compose exec web ls -la /app/staticfiles
```

## Очистка

### Удаление контейнеров

```bash
# Stop and remove
docker-compose down

# Remove with volumes
docker-compose down -v

# Remove all volumes manually
docker volume rm sales_postgres_data sales_static_volume sales_media_volume
```

### Очистка образов

```bash
# Remove image
docker rmi sales-app:latest

# Remove all unused images
docker image prune

# Remove all images
docker rmi $(docker images -q)
```

### Очистка всего

```bash
# Полная очистка (осторожно!)
docker-compose down -v
docker system prune -a --volumes
```

## Миграция данных

### From SQLite to PostgreSQL

#### Option 1: Автоматическая (через entrypoint)

Контейнер автоматически выполнит миграции при старте.

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
```

#### Option 2: Ручная с экспортом-импортом

```bash
# 1. Export from SQLite
docker exec sales_web_app python manage.py dumpdata \
  --exclude auth.permission \
  --exclude contenttypes \
  > data.json

# 2. Setup PostgreSQL in .env and docker-compose up

# 3. Import to PostgreSQL
docker-compose exec web python manage.py loaddata /tmp/data.json
```

#### Option 3: Скрипт миграции

```bash
docker-compose exec web python migrate_sqlite_to_postgres.py
```

## Производство - Best Practices

### 1. Безопасность

```env
DEBUG=False
DJANGO_SECRET_KEY=<generate-new-random-key>
ALLOWED_HOSTS=yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 2. Performance

```bash
# Используйте production-ready сервер
# В Dockerfile CMD: gunicorn sales_project.wsgi --workers 4 --bind 0.0.0.0:8000

# Используйте Nginx для serve статики
# Включите gzip compression

# Используйте CDN для статики
```

### 3. Мониторинг

```bash
# Setup logging
# docker-compose logs -f > /var/log/sales-app.log

# Health check
# curl http://localhost/health/

# Metrics
# Добавьте prometheus endpoints
```

### 4. Backup

```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U postgres sales_db > backup.sql

# Backup volumes
docker run --rm -v sales_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/db-backup.tar.gz /data
```

## Useful Docker Commands Reference

```bash
# Показать образы
docker images

# Показать контейнеры (все)
docker ps -a

# Удалить образ
docker rmi <image-id>

# Удалить контейнер
docker rm <container-id>

# Build image
docker build -t <name>:<tag> .

# Run контейнер
docker run -d -p 8000:8000 <image>

# Execute в контейнере
docker exec -it <container> bash

# Copy файлы
docker cp <container>:/path/to/file ./local/path

# View image layers
docker history <image>

# Save image
docker save <image> > image.tar

# Load image
docker load < image.tar
```

---

Для дополнительной помощи см. README.md или откройте Issue в GitHub.
