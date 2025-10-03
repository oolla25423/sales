from django.db import models
import uuid

# Create your models here.
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=200, verbose_name="Название продукта")
    quantity = models.IntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    sale_date = models.DateTimeField(verbose_name="Дата продажи")
    customer_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    customer_email = models.EmailField(verbose_name="Электронная почта клиента")
    
    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
    
    def __str__(self):
        return f"{self.product_name} - {self.sale_date}"
    
    def to_dict(self):
        """Преобразовать экземпляр модели в словарь для сериализации JSON"""
        return {
            'id': str(self.id),
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price),
            'sale_date': self.sale_date.isoformat(),
            'customer_name': self.customer_name,
            'customer_email': self.customer_email
        }