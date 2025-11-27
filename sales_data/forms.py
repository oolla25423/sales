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
    # Явно задаём поле sale_date с форматами, совместимыми с HTML5 `datetime-local`.
    sale_date = forms.DateTimeField(
        label='Дата продажи',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'},
            format='%Y-%m-%dT%H:%M'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing instance, format initial sale_date for datetime-local input
        try:
            inst = kwargs.get('instance') or getattr(self, 'instance', None)
            if inst and getattr(inst, 'sale_date', None):
                dt = inst.sale_date
                # If datetime has tzinfo, convert to local time to display, otherwise use as is
                try:
                    if dt.tzinfo is not None:
                        dt = dt.astimezone()
                except Exception:
                    pass
                self.initial['sale_date'] = dt.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            pass

    class Meta:
        model = Sale
        fields = ['product_name', 'quantity', 'price', 'sale_date', 'customer_name', 'customer_email']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            # sale_date вынесено отдельно выше, чтобы задать формат корректно
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