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