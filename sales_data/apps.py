from django.apps import AppConfig

class SalesDataConfig(AppConfig):
    """Конфигурация приложения данных о продажах"""
    name = 'sales_data'
    # Удалено default_auto_field, так как мы не используем базу данных