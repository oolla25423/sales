from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product_name', 'quantity', 'price', 'sale_date', 'customer_name', 'customer_email']
        widgets = {
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'product_name': 'Название продукта',
            'quantity': 'Количество',
            'price': 'Цена',
            'sale_date': 'Дата продажи',
            'customer_name': 'Имя клиента',
            'customer_email': 'Электронная почта клиента',
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return quantity
    
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price
    
    def clean_customer_email(self):
        email = self.cleaned_data['customer_email']
        # Basic email validation
        if '@' not in email:
            raise forms.ValidationError("Введите действительный адрес электронной почты.")
        return email