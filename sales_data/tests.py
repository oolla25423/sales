from django.test import TestCase
from django.urls import reverse
from .models import Sale
from .forms import SaleForm, SaleEditForm
import uuid
from datetime import datetime

class SaleModelTest(TestCase):
    def setUp(self):
        self.sale = Sale.objects.create(
            product_name="Тестовый продукт",
            quantity=5,
            price=100.50,
            sale_date=datetime.now(),
            customer_name="Тестовый клиент",
            customer_email="test@example.com"
        )
    
    def test_sale_creation(self):
        self.assertTrue(isinstance(self.sale, Sale))
        self.assertEqual(str(self.sale), "Тестовый продукт - Тестовый клиент")
    
    def test_sale_to_dict(self):
        sale_dict = self.sale.to_dict()
        self.assertIsInstance(sale_dict, dict)
        self.assertIn('product_name', sale_dict)
        self.assertIn('quantity', sale_dict)
        self.assertIn('price', sale_dict)
        self.assertIn('sale_date', sale_dict)
        self.assertIn('customer_name', sale_dict)
        self.assertIn('customer_email', sale_dict)

class SaleFormTest(TestCase):
    def test_sale_form_valid_data(self):
        form_data = {
            'product_name': 'Тестовый продукт',
            'quantity': 5,
            'price': 100.50,
            'sale_date': datetime.now(),
            'customer_name': 'Тестовый клиент',
            'customer_email': 'test@example.com'
        }
        form = SaleForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_sale_form_invalid_data(self):
        form_data = {
            'product_name': 'Тестовый продукт',
            'quantity': -1,
            'price': 100.50,
            'sale_date': datetime.now(),
            'customer_name': 'Тестовый клиент',
            'customer_email': 'invalid-email'
        }
        form = SaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertIn('customer_email', form.errors)

class ViewsTest(TestCase):
    def test_index_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Управление данными о продажах")
    
    def test_add_sale_view_get(self):
        """Тест GET запроса к странице добавления продажи"""
        response = self.client.get(reverse('add_sale'))
        self.assertEqual(response.status_code, 200)
    
    def test_search_sales_view(self):
        """Тест поиска продаж"""
        response = self.client.get(reverse('search_sales'), {'q': 'тест'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')