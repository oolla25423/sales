"""
Конфигурация ASGI для проекта sales_project.

Он предоставляет вызываемый ASGI как переменную уровня модуля с именем ``application``.

Для получения дополнительной информации о данном файле, см.
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_project.settings')

application = get_asgi_application()