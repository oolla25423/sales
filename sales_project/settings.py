"""
Настройки Django для проекта sales_project.

Сгенерировано с помощью 'django-admin startproject' с использованием Django 5.2.6.

Для получения дополнительной информации о данном файле, см.
https://docs.djangoproject.com/en/5.2/topics/settings/

Полный список настроек и их значений, см.
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Построение путей внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Настройки быстрого запуска разработки - непригодны для производства
# См. https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: храните секретный ключ, используемый в производстве, в секрете!
SECRET_KEY = 'django-insecure-qt!4w=!5+^@ly1qu7qb!od%kqix6#q--59fhp!!nhm3+2=1=ql'

# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: не запускайте с включенной отладкой в производстве!
DEBUG = True

ALLOWED_HOSTS = []


# Определение приложения

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sales_data',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sales_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sales_project.wsgi.application'


# База данных
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Конфигурация базы данных не требуется, так как мы не используем базу данных
DATABASES = {}


# Проверка пароля
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Интернационализация
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Статические файлы (CSS, JavaScript, Изображения)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'sales_data' / 'static',
]


# Тип поля первичного ключа по умолчанию
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

# Удалено DEFAULT_AUTO_FIELD, так как мы не используем базу данных