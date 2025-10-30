from django import forms
from .models import Sale

class FileSaleForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    product_name = forms.CharField(
        max_length=200,
        label='Название продукта',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        label='Количество',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Цена (руб.)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    sale_date = forms.DateTimeField(
        label='Дата продажи',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    customer_name = forms.CharField(
        max_length=200,
        label='Имя клиента',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_email = forms.EmailField(
        label='Электронная почта клиента',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def clean_quantity(self):
        """Проверка количества"""
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return quantity
    
    def clean_price(self):
        """Проверка цены"""
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price

class SaleForm(forms.Form):
    product_name = forms.CharField(
        max_length=200,
        label='Название продукта',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        label='Количество',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Цена (руб.)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    sale_date = forms.DateTimeField(
        label='Дата продажи',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    customer_name = forms.CharField(
        max_length=200,
        label='Имя клиента',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_email = forms.EmailField(
        label='Электронная почта клиента',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def clean_quantity(self):
        """Проверка количества"""
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return quantity
    
    def clean_price(self):
        """Проверка цены"""
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price
    
    def clean_customer_email(self):
        """Проверка электронной почты"""
        email = self.cleaned_data['customer_email']
        # Базовая проверка электронной почты
        if '@' not in email:
            raise forms.ValidationError("Введите действительный адрес электронной почты.")
        return email

class SaleEditForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product_name', 'quantity', 'price', 'sale_date', 'customer_name', 'customer_email']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product_name': 'Название продукта',
            'quantity': 'Количество',
            'price': 'Цена (руб.)',
            'sale_date': 'Дата продажи',
            'customer_name': 'Имя клиента',
            'customer_email': 'Электронная почта клиента',
        }
    
    def clean_quantity(self):
        """Проверка количества"""
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля.")
        return quantity
    
    def clean_price(self):
        """Проверка цены"""
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price