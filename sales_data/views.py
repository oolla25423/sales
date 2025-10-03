import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from .models import Sale
from .forms import SaleForm
import uuid

# Define upload directory
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def index(request):
    """Главная страница с формой и списком файлов"""
    sales = []
    
    # Получить список существующих файлов
    json_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.json')]
    xml_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.xml')]
    
    # Получить все продажи из базы данных
    db_sales = Sale.objects.all()
    for sale in db_sales:
        sales.append(sale.to_dict())
    
    # Попытаться загрузить данные о продажах из файлов
    try:
        # Загрузить из JSON файлов
        for filename in json_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        sales.extend(data)
                    elif isinstance(data, dict):
                        sales.append(data)
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
                    sales.append(sale_data)
            except ET.ParseError:
                pass
    except Exception as e:
        pass
    
    return render(request, 'sales_data/index.html', {
        'form': SaleForm(),
        'json_files': json_files,
        'xml_files': xml_files,
        'sales': sales,
        'db_sales': db_sales  # Передаем отдельно для возможности удаления
    })

def add_sale(request):
    """Добавить новую продажу через форму и сохранить как JSON или XML"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save()
            
            # Определить формат (JSON или XML)
            format_type = request.POST.get('format', 'json')
            
            # Создать словарь данных
            sale_data = sale.to_dict()
            
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
                
                # Не показываем сообщение об успешном сохранении
            except Exception as e:
                # Не показываем сообщение об ошибке
                pass
            
            return redirect('index')
        else:
            # Не показываем сообщение об ошибках в форме
            pass
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
                # Не показываем сообщение об ошибке
                return redirect('index')
            
            # Сохранить файл
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            # Не показываем сообщение об успешной загрузке
        except (json.JSONDecodeError, ET.ParseError) as e:
            # Не показываем сообщение об ошибке
            # Удалить недействительный файл, если он был создан
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            # Не показываем сообщение об ошибке
            # Удалить файл, если он был создан
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return redirect('index')

def download_file(request, filename):
    """Скачать определенный файл"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        # Не показываем сообщение об ошибке
        return redirect('index')
    
    if not (filename.endswith('.json') or filename.endswith('.xml')):
        # Не показываем сообщение об ошибке
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
        # Не показываем сообщение об успешном удалении
    else:
        # Не показываем сообщение об ошибке
        pass
    
    return redirect('index')

def delete_sale(request, sale_id):
    """Удалить запись о продаже из базы данных"""
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    return redirect('index')