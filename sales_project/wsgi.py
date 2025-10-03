"""
Конфигурация WSGI для проекта sales_project.

Он предоставляет вызываемый WSGI как переменную уровня модуля с именем ``application``.

Для получения дополнительной информации о данном файле, см.
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_project.settings')

application = get_wsgi_application()