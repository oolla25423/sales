import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
import uuid
from .forms import SaleForm, SaleEditForm
from .models import SaleData, Sale

# Определить директорию загрузки
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def index(request):
    """Главная страница с формой и списком файлов"""
    sales_from_files = []
    sales_from_db = []
    all_sales = []
    
    # Получить поисковый запрос
    search_query = request.GET.get('q', '')
    search_query_cf = search_query.casefold() if search_query else ''

    # Источник отображения: all | file | database
    source = request.GET.get('source', 'all')
    
    # Загрузить данные о продажах из файлов
    json_files = []
    xml_files = []
    try:
        # Получить список существующих файлов
        json_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.json')]
        xml_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.xml')]
        
        # Загрузить из JSON файлов
        for filename in json_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            # Применить поиск, если есть запрос (без учета регистра)
                            if not search_query or (
                                search_query_cf in str(item.get('product_name', '') or '').casefold() or
                                search_query_cf in str(item.get('customer_name', '') or '').casefold() or
                                search_query_cf in str(item.get('customer_email', '') or '').casefold()
                            ):
                                item['source'] = 'file'
                                sales_from_files.append(item)
                    elif isinstance(data, dict):
                        # Применить поиск, если есть запрос (без учета регистра)
                        if not search_query or (
                            search_query_cf in str(data.get('product_name', '') or '').casefold() or
                            search_query_cf in str(data.get('customer_name', '') or '').casefold() or
                            search_query_cf in str(data.get('customer_email', '') or '').casefold()
                        ):
                            data['source'] = 'file'
                            sales_from_files.append(data)
                except json.JSONDecodeError:
                    pass
        
        # Загрузить из XML файлов
        for filename in xml_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                for sale_elem in root.findall('sale'):
                    sale_data = {}
                    for child in sale_elem:
                        sale_data[child.tag] = child.text
                    
                    # Применить поиск, если есть запрос (без учета регистра)
                    if not search_query or (
                        search_query_cf in str(sale_data.get('product_name', '') or '').casefold() or
                        search_query_cf in str(sale_data.get('customer_name', '') or '').casefold() or
                        search_query_cf in str(sale_data.get('customer_email', '') or '').casefold()
                    ):
                        sale_data['source'] = 'file'
                        sales_from_files.append(sale_data)
            except ET.ParseError:
                pass
    except Exception as e:
        pass
    
    # Загрузить данные из базы данных
    try:
        db_sales = Sale.objects.all()
        # Применить поиск, если есть запрос (без учета регистра)
        if search_query:
            # Case-insensitive (Unicode-aware) filtering in Python
            db_sales = [s for s in db_sales if (
                search_query_cf in (s.product_name or '').casefold() or
                search_query_cf in (s.customer_name or '').casefold() or
                search_query_cf in (s.customer_email or '').casefold()
            )]
        
        for sale in db_sales:
            sale_dict = sale.to_dict()
            sale_dict['source'] = 'database'
            sales_from_db.append(sale_dict)
    except Exception as e:
        pass
    
    # Объединить данные из файлов и базы данных
    if source == 'database':
        all_sales = sales_from_db
    elif source == 'file':
        all_sales = sales_from_files
    else:
        all_sales = sales_from_files + sales_from_db
    
    return render(request, 'sales_data/index.html', {
        'form': SaleForm(),
        'all_sales': all_sales,
        'sales_from_files': sales_from_files,
        'sales_from_db': sales_from_db,
        'search_query': search_query,
        'json_files': json_files,
        'xml_files': xml_files,
        'current_source': source,
    })

def add_sale(request):
    """Добавить новую продажу через форму и сохранить как JSON/XML или в базу данных"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            # Определить, куда сохранять данные: в файл или в базу данных
            save_to = request.POST.get('save_to', 'file')
            
            if save_to == 'database':
                # Сохранить в базу данных
                try:
                    # Проверить на дубликаты
                    existing_sale = Sale.objects.filter(
                        product_name=form.cleaned_data['product_name'],
                        customer_email=form.cleaned_data['customer_email'],
                        sale_date=form.cleaned_data['sale_date']
                    ).first()
                    
                    if existing_sale:
                        messages.error(request, 'Запись с такими данными уже существует в базе данных.')
                    else:
                        # Создать новую запись
                        sale = Sale(
                            product_name=form.cleaned_data['product_name'],
                            quantity=form.cleaned_data['quantity'],
                            price=form.cleaned_data['price'],
                            sale_date=form.cleaned_data['sale_date'],
                            customer_name=form.cleaned_data['customer_name'],
                            customer_email=form.cleaned_data['customer_email']
                        )
                        sale.save()
                        messages.success(request, 'Данные успешно сохранены в базе данных.')
                except Exception as e:
                    messages.error(request, 'Ошибка при сохранении данных в базу данных.')
            else:
                # Сохранить в файл (JSON или XML)
                # Создать словарь данных из формы (без сохранения в базу данных)
                sale_data = {
                    'id': str(uuid.uuid4()),
                    'product_name': form.cleaned_data['product_name'],
                    'quantity': form.cleaned_data['quantity'],
                    'price': float(form.cleaned_data['price']),
                    'sale_date': form.cleaned_data['sale_date'].isoformat(),
                    'customer_name': form.cleaned_data['customer_name'],
                    'customer_email': form.cleaned_data['customer_email']
                }
                
                # Определить формат (JSON или XML)
                format_type = request.POST.get('format', 'json')
                
                # Сгенерировать имя файла
                filename = f"sale_{uuid.uuid4().hex}.{format_type}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                try:
                    if format_type == 'json':
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(sale_data, f, indent=2, ensure_ascii=False)
                    else:  # XML
                        root = ET.Element('sale')
                        for key, value in sale_data.items():
                            elem = ET.SubElement(root, key)
                            elem.text = str(value)
                        tree = ET.ElementTree(root)
                        tree.write(filepath, encoding='utf-8', xml_declaration=True)
                    
                    messages.success(request, f'Данные успешно сохранены в файл {filename}.')
                except Exception as e:
                    messages.error(request, 'Ошибка при сохранении данных в файл.')
            
            return redirect('index')
        else:
            # Показываем сообщение об ошибках в форме
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = SaleForm()
    
    return render(request, 'sales_data/index.html', {'form': form})

def upload_file(request):
    """Загрузить JSON или XML файл"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        filename = uploaded_file.name
        
        # Очистить имя файла
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename = f"{uuid.uuid4().hex}_{filename}"
        
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        try:
            # Сохранить файл
            file_content = uploaded_file.read()
            
            # Проверить содержимое файла в зависимости от расширения
            if filename.endswith('.json'):
                # Проверить JSON
                json.loads(file_content.decode('utf-8'))
            elif filename.endswith('.xml'):
                # Проверить XML
                ET.fromstring(file_content)
            else:
                messages.error(request, 'Неподдерживаемый формат файла.')
                return redirect('index')
            
            # Сохранить файл
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            messages.success(request, 'Файл успешно загружен.')
        except (json.JSONDecodeError, ET.ParseError) as e:
            # Удалить недействительный файл, если он был создан
            if os.path.exists(filepath):
                os.remove(filepath)
            messages.error(request, 'Недопустимый файл. Файл удален.')
        except Exception as e:
            # Удалить файл, если он был создан
            if os.path.exists(filepath):
                os.remove(filepath)
            messages.error(request, 'Ошибка при загрузке файла.')
    
    return redirect('index')

def download_file(request, filename):
    """Скачать определенный файл"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        messages.error(request, 'Файл не найден.')
        return redirect('index')
    
    if not (filename.endswith('.json') or filename.endswith('.xml')):
        messages.error(request, 'Недопустимый файл.')
        return redirect('index')
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

def delete_file(request, filename):
    """Удалить определенный файл"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        messages.success(request, 'Файл успешно удален.')
    else:
        messages.error(request, 'Файл не найден.')
    
    return redirect('index')

def delete_sale(request, sale_id):
    """Удалить запись о продаже из файлов"""
    # Найти и удалить файл, содержащий запись о продаже с указанным ID
    try:
        # Поиск в JSON файлах
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get('id') == sale_id:
                            os.remove(filepath)
                            messages.success(request, 'Запись успешно удалена.')
                            break
                        elif isinstance(data, list):
                            # Если файл содержит список продаж, нужно удалить конкретную продажу
                            for i, sale in enumerate(data):
                                if isinstance(sale, dict) and sale.get('id') == sale_id:
                                    data.pop(i)
                                    # Перезаписать файл без удаленной продажи
                                    with open(filepath, 'w', encoding='utf-8') as f_out:
                                        json.dump(data, f_out, indent=2, ensure_ascii=False)
                                    messages.success(request, 'Запись успешно удалена.')
                                    break
                except (json.JSONDecodeError, IOError):
                    pass
        
        # Поиск в XML файлах
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.xml'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    # Если корневой элемент - sale с нужным ID
                    id_elem = root.find('id')
                    if root.tag == 'sale' and id_elem is not None and id_elem.text == sale_id:
                        os.remove(filepath)
                        messages.success(request, 'Запись успешно удалена.')
                    # Если корневой элемент содержит несколько sale
                    else:
                        deleted = False
                        for sale_elem in root.findall('sale'):
                            id_elem = sale_elem.find('id')
                            if id_elem is not None and id_elem.text == sale_id:
                                root.remove(sale_elem)
                                deleted = True
                        if deleted:
                            tree.write(filepath, encoding='utf-8', xml_declaration=True)
                            messages.success(request, 'Запись успешно удалена.')
                except (ET.ParseError, IOError):
                    pass
    except Exception as e:
        messages.error(request, 'Ошибка при удалении записи.')
    
    return redirect('index')

# Новые функции для работы с базой данных

def search_sales(request):
    """AJAX поиск по записям в базе данных"""
    query = request.GET.get('q', '')
    sales = Sale.objects.all()
    
    if query:
        # Case-insensitive (Unicode-aware) filtering in Python
        query_cf = query.casefold()
        sales = [s for s in sales if (
            query_cf in (s.product_name or '').casefold() or
            query_cf in (s.customer_name or '').casefold() or
            query_cf in (s.customer_email or '').casefold()
        )]
    
    # Преобразовать в список словарей для JSON ответа
    sales_data = [sale.to_dict() for sale in sales]
    
    return JsonResponse({'sales': sales_data})

def edit_sale(request, sale_id):
    """Редактировать запись о продаже в базе данных"""
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        form = SaleEditForm(request.POST, instance=sale)
        if form.is_valid():
            # Проверить на дубликаты (кроме текущей записи)
            existing_sale = Sale.objects.filter(
                product_name=form.cleaned_data['product_name'],
                customer_email=form.cleaned_data['customer_email'],
                sale_date=form.cleaned_data['sale_date']
            ).exclude(id=sale_id).first()
            
            if existing_sale:
                messages.error(request, 'Запись с такими данными уже существует в базе данных.')
            else:
                form.save()
                messages.success(request, 'Запись успешно обновлена.')
                return redirect('index')
    else:
        form = SaleEditForm(instance=sale)
    
    return render(request, 'sales_data/edit_sale.html', {'form': form, 'sale': sale})

def delete_db_sale(request, sale_id):
    """Удалить запись о продаже из базы данных"""
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    messages.success(request, 'Запись успешно удалена из базы данных.')
    return redirect('index')