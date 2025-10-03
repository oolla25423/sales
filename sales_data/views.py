import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import uuid
from .forms import SaleForm
from .models import SaleData

# Определить директорию загрузки
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def index(request):
    """Главная страница с формой и списком файлов"""
    sales = []
    
    # Получить список существующих файлов
    json_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.json')]
    xml_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.xml')]
    
    # Загрузить данные о продажах только из файлов (не из базы данных)
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
        'sales': sales
    })

def add_sale(request):
    """Добавить новую продажу через форму и сохранить как JSON или XML"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
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
                            break
                        elif isinstance(data, list):
                            # Если файл содержит список продаж, нужно удалить конкретную продажу
                            for i, sale in enumerate(data):
                                if isinstance(sale, dict) and sale.get('id') == sale_id:
                                    data.pop(i)
                                    # Перезаписать файл без удаленной продажи
                                    with open(filepath, 'w', encoding='utf-8') as f_out:
                                        json.dump(data, f_out, indent=2, ensure_ascii=False)
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
                except (ET.ParseError, IOError):
                    pass
    except Exception as e:
        pass
    
    return redirect('index')