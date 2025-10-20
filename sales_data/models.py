from django.db import models
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import Manager
    from django.db.models import QuerySet

# Простая структура данных для продаж (без модели базы данных)
class SaleData:
    """Класс для представления данных о продаже без использования базы данных"""
    
    def __init__(self, id, product_name, quantity, price, sale_date, customer_name, customer_email):
        self.id = id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.sale_date = sale_date
        self.customer_name = customer_name
        self.customer_email = customer_email
    
    def to_dict(self):
        """Преобразовать экземпляр в словарь для сериализации"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': self.price,
            'sale_date': self.sale_date,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создать экземпляр из словаря"""
        return cls(
            id=data.get('id'),
            product_name=data.get('product_name'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            sale_date=data.get('sale_date'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email')
        )

# Модель Django для хранения данных о продажах в базе данных
class Sale(models.Model):
    if TYPE_CHECKING:
        objects: Manager  # type: ignore
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField()
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    
    class Meta:
        db_table = 'sales'
        unique_together = ('product_name', 'customer_email', 'sale_date')
    
    def __str__(self):
        return f"{self.product_name} - {self.customer_name}"
    
    def to_dict(self):
        """Преобразовать экземпляр модели в словарь"""
        from decimal import Decimal
        # At runtime, self.price will be a Decimal and self.sale_date will be a datetime
        # But type checkers see them as Field instances, so we need to handle both cases
        return {
            'id': str(self.id),
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price) if isinstance(self.price, Decimal) else str(self.price),  # type: ignore
            'sale_date': self.sale_date.isoformat() if hasattr(self.sale_date, 'isoformat') else str(self.sale_date),  # type: ignore
            'customer_name': self.customer_name,
            'customer_email': self.customer_email
        }