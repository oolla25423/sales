from django.apps import AppConfig
from django.utils.functional import cached_property

class SalesDataConfig(AppConfig):
    """Конфигурация приложения данных о продажах"""
    
    @cached_property
    def default_auto_field(self):
        return 'django.db.models.BigAutoField'
        
    name = 'sales_data'