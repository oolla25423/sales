# Система управления данными о продажах

Веб-приложение на Django для управления данными о продажах с поддержкой контейнеризации и PostgreSQL.

## Возможности

- ✅ Добавление информации о продажах через веб-форму
- ✅ Сохранение данных в базе данных (SQLite или PostgreSQL)
- ✅ Просмотр, редактирование и удаление записей
- ✅ AJAX-поиск по записям
- ✅ Поддержка импорта/экспорта (XML, JSON)
- ✅ Проверка на дубликаты
- ✅ Контейнеризация с Docker
- ✅ Multi-container setup с Docker Compose

## Структура проекта

```
sales/
├── Dockerfile                    # Образ Docker для Django приложения
├── docker-compose.yml            # Оркестрация контейнеров
├── .dockerignore                 # Исключения для Docker
├── .env.example                  # Пример переменных окружения
├── entrypoint.sh                 # Скрипт инициализации контейнера
├── nginx.conf                    # Конфигурация Nginx для production
├── migrate_sqlite_to_postgres.py # Скрипт миграции данных
├── manage.py                     # Django управление
├── requirements.txt              # Python зависимости
├── db.sqlite3                    # SQLite база (только для разработки)
│
├── sales_data/                   # Django приложение
│   ├── models.py                 # Модели данных
│   ├── views.py                  # Представления
│   ├── forms.py                  # Формы
│   ├── urls.py                   # URL маршруты
│   ├── tests.py                  # Тесты
│   ├── migrations/               # Миграции БД
│   ├── templates/                # HTML шаблоны
│   ├── static/                   # CSS, JS, изображения
│   └── fixtures/                 # Тестовые данные
│
├── sales_project/                # Конфигурация проекта
│   ├── settings.py               # Настройки Django
│   ├── urls.py                   # Главные URL маршруты
│   ├── wsgi.py                   # WSGI приложение
│   └── asgi.py                   # ASGI приложение
│
└── staticfiles/                  # Собранные статические файлы
```

## Быстрый старт

### Вариант 1: Локальная разработка (SQLite)

#### Требования
- Python 3.11+
- pip

#### Установка

```bash
# 1. Клонируем репозиторий
git clone https://github.com/yourusername/sales.git
cd sales

# 2. Создаем виртуальное окружение
python -m venv venv

# 3. Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Устанавливаем зависимости
pip install -r requirements.txt

# 5. Запускаем миграции
python manage.py migrate

# 6. (Опционально) Создаем суперпользователя
python manage.py createsuperuser

# 7. Запускаем разработчицкий сервер
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

### Вариант 2: Docker (SQLite)

```bash
# 1. Создаем .env файл
cp .env.example .env

# 2. Собираем и запускаем контейнер (только web, без БД)
docker build -t sales-app .
docker run -p 8000:8000 -v $(pwd):/app sales-app

# На Windows PowerShell:
docker run -p 8000:8000 -v ${PWD}:/app sales-app
```

### Вариант 3: Docker Compose (Рекомендуется для production)

#### Требования
- Docker 20.10+
- Docker Compose 1.29+

#### Для разработки (с SQLite)

```bash
# 1. Создаем .env файл
cp .env.example .env
# Отредактируйте .env по необходимости (опционально)

# 2. Собираем образ и запускаем контейнеры
docker-compose up --build

# Приложение будет доступно по адресу: http://localhost:8000/
```

#### Для production (с PostgreSQL)

```bash
# 1. Создаем .env файл с PostgreSQL конфигурацией
cp .env.example .env

# 2. Отредактируйте .env:
# DEBUG=False
# DJANGO_SECRET_KEY=your-very-secret-key-here
# DB_ENGINE=django.db.backends.postgresql
# DB_PASSWORD=your-strong-password

# 3. Собираем и запускаем контейнеры
docker-compose up -d --build

# 4. Проверяем логи
docker-compose logs -f web

# 5. Останавливаем приложение
docker-compose down
```

#### С Nginx (production)

```bash
# Запускаем с production профилем, который включит Nginx
docker-compose --profile production up -d --build

# Приложение будет доступно по адресу: http://localhost/
```

## Переменные окружения

Все переменные определены в файле `.env`. Пример конфигурации:

```env
# Django
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# PostgreSQL (для Docker)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Для локальной разработки (SQLite)
# DB_ENGINE=django.db.backends.sqlite3
```

**Важно:** 
- Никогда не коммитьте файл `.env` в git
- Используйте только `.env.example` в репозитории
- Генерируйте новый `DJANGO_SECRET_KEY` для production:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

## Миграция данных: SQLite → PostgreSQL

### Автоматическая миграция

```bash
# Запускаем скрипт миграции
python migrate_sqlite_to_postgres.py
```

### Процесс миграции через Docker

```bash
# 1. Убедитесь, что контейнеры работают
docker-compose ps

# 2. Запустите миграции в контейнере Django
docker-compose exec web python migrate_sqlite_to_postgres.py

# 3. Проверьте логи
docker-compose logs -f web
```

### Ручная миграция

```bash
# 1. Экспортируем данные из SQLite
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json

# 2. Переключаемся на PostgreSQL в .env
# DB_ENGINE=django.db.backends.postgresql
# DB_HOST=localhost
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_NAME=sales_db

# 3. Импортируем данные в PostgreSQL
python manage.py loaddata data.json
```

## Использование приложения

### Главная страница
Перейдите по адресу http://localhost:8000/ (или http://localhost/ для production)

### Функции

1. **Добавление записи**
   - Заполните форму с деталями продажи
   - Нажмите "Добавить"
   - Данные сохранятся в БД

2. **Поиск**
   - Используйте поле поиска для быстрого нахождения записей
   - Поиск работает в реальном времени (AJAX)

3. **Редактирование**
   - Нажмите на кнопку "Редактировать" рядом с записью
   - Отредактируйте данные
   - Нажмите "Сохранить"

4. **Удаление**
   - Нажмите на кнопку "Удалить"
   - Подтвердите удаление

### Структура записи о продаже

Каждая запись содержит:
- **Название продукта** - наименование товара
- **Количество** - количество единиц
- **Цена** - цена за единицу
- **Дата продажи** - дата совершения продажи
- **Имя клиента** - ФИО покупателя
- **Email клиента** - электронная почта

## Администратор

Доступ к админ-панели: http://localhost:8000/admin/

```bash
# Создание суперпользователя (локально)
python manage.py createsuperuser

# В Docker контейнере
docker-compose exec web python manage.py createsuperuser

# Или установите CREATE_SUPERUSER=true в .env для автоматического создания
```

## Работа с контейнерами

### Полезные команды Docker Compose

```bash
# Запуск всех сервисов
docker-compose up

# Запуск в фоне
docker-compose up -d

# Остановка
docker-compose stop

# Остановка и удаление контейнеров
docker-compose down

# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web

# Выполнить команду в контейнере
docker-compose exec web python manage.py shell

# Перестроить образ
docker-compose build --no-cache

# Удалить все (контейнеры, сеть, volumes)
docker-compose down -v
```

### Управление базой данных

```bash
# Создание миграции
docker-compose exec web python manage.py makemigrations

# Применение миграций
docker-compose exec web python manage.py migrate

# Просмотр статуса миграций
docker-compose exec web python manage.py showmigrations

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Экспорт данных
docker-compose exec web python manage.py dumpdata > data.json

# Импорт данных
docker-compose exec web python manage.py loaddata data.json
```

## Тестирование

```bash
# Запуск тестов локально
python manage.py test

# Запуск тестов в Docker
docker-compose exec web python manage.py test

# Запуск конкретного теста
docker-compose exec web python manage.py test sales_data.tests.TestSaleModel
```

## Производство (Production)

### Настройка для Production

1. **Генерируем новый SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Обновляем .env**
   ```env
   DEBUG=False
   DJANGO_SECRET_KEY=your-generated-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DB_ENGINE=django.db.backends.postgresql
   DB_PASSWORD=strong-password-here
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

3. **Запускаем с Nginx**
   ```bash
   docker-compose --profile production up -d --build
   ```

4. **Проверяем статус**
   ```bash
   docker-compose ps
   docker-compose logs -f web
   ```

## Структура БД

### Модель Sale

```python
class Sale(models.Model):
    product_name = CharField(max_length=255)
    quantity = IntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)
    sale_date = DateField()
    client_name = CharField(max_length=255)
    client_email = EmailField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Проблемы и решения

### Контейнер не запускается

```bash
# 1. Проверяем логи
docker-compose logs web

# 2. Перестраиваем образ
docker-compose build --no-cache

# 3. Удаляем старые контейнеры
docker-compose down -v
docker-compose up --build
```

### Ошибка при подключении к БД

```bash
# Убедитесь, что PostgreSQL контейнер работает
docker-compose ps

# Проверьте переменные окружения в .env
docker-compose config | grep DB_

# Переподключитесь
docker-compose exec web python manage.py migrate
```

### Статические файлы не загружаются

```bash
# Пересоберите статические файлы
docker-compose exec web python manage.py collectstatic --noinput

# Перезагрузите контейнер
docker-compose restart web
```

## Развертывание на облачных платформах

### Render (бывший Heroku)
1. Подключитесь к GitHub репозиторию
2. Установите переменные окружения в Render
3. Выберите PostgreSQL как БД
4. Deploy будет автоматическим при push в main

### AWS, Azure, Google Cloud
Используйте Docker образы с Container Registry и K8s для оркестрации

## Вклад

Для внесения изменений:
1. Создайте новую ветку (`git checkout -b feature/NewFeature`)
2. Коммитьте изменения (`git commit -m 'Add NewFeature'`)
3. Загрузите ветку (`git push origin feature/NewFeature`)
4. Откройте Pull Request

## Лицензия

MIT License - см. LICENSE файл

## Автор

Ваше имя / Организация

## Поддержка

Для вопросов и проблем откройте Issue в GitHub репозитории.
