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
from .forms import SaleForm, SaleEditForm, FileSaleForm
from .models import SaleData, Sale

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def index(request):
    sales_from_files = []
    sales_from_db = []
    all_sales = []
    
    search_query = request.GET.get('q', '')
    search_query_cf = search_query.casefold() if search_query else ''

    source = request.GET.get('source', 'all')
    
    def _parse_date(value):
        if not value:
            return value
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
        formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d.%m.%Y %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return value

    json_files = []
    xml_files = []
    try:
        json_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.json')]
        xml_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.xml')]
        
        for filename in json_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if 'sale_date' in item and isinstance(item['sale_date'], str):
                                try:
                                    item['sale_date'] = datetime.fromisoformat(item['sale_date'])
                                except ValueError:
                                    item['sale_date'] = _parse_date(item.get('sale_date'))
                            
                            if not search_query or (
                                search_query_cf in str(item.get('product_name', '') or '').casefold() or
                                search_query_cf in str(item.get('customer_name', '') or '').casefold() or
                                search_query_cf in str(item.get('customer_email', '') or '').casefold()
                            ):
                                item['source'] = 'file'
                                sales_from_files.append(item)
                    elif isinstance(data, dict):
                        if 'sale_date' in data and isinstance(data['sale_date'], str):
                            try:
                                data['sale_date'] = datetime.fromisoformat(data['sale_date'])
                            except ValueError:
                                data['sale_date'] = _parse_date(data.get('sale_date'))
                        
                        if not search_query or (
                            search_query_cf in str(data.get('product_name', '') or '').casefold() or
                            search_query_cf in str(data.get('customer_name', '') or '').casefold() or
                            search_query_cf in str(data.get('customer_email', '') or '').casefold()
                        ):
                            data['source'] = 'file'
                            sales_from_files.append(data)
                except json.JSONDecodeError:
                    pass
        
        for filename in xml_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                if root.tag == 'sale':
                    sale_data = {}
                    for child in root:
                        if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                            sale_data[child.tag] = _parse_date(child.text)
                        else:
                            sale_data[child.tag] = child.text
                    
                    if 'sale_date' in sale_data and isinstance(sale_data['sale_date'], str):
                        sale_data['sale_date'] = _parse_date(sale_data['sale_date'])
                    
                    if not search_query or (
                        search_query_cf in str(sale_data.get('product_name', '') or '').casefold() or
                        search_query_cf in str(sale_data.get('customer_name', '') or '').casefold() or
                        search_query_cf in str(sale_data.get('customer_email', '') or '').casefold()
                    ):
                        sale_data['source'] = 'file'
                        sales_from_files.append(sale_data)
                else:
                    for sale_elem in root.findall('sale'):
                        sale_data = {}
                        for child in sale_elem:
                            if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                                sale_data[child.tag] = _parse_date(child.text)
                            else:
                                sale_data[child.tag] = child.text
                        
                        if 'sale_date' in sale_data and isinstance(sale_data['sale_date'], str):
                            sale_data['sale_date'] = _parse_date(sale_data['sale_date'])
                        
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
        messages.error(request, f"Error reading files: {str(e)}")
    
    try:
        db_sales = Sale.objects.all()
        if search_query:
            db_sales = [s for s in db_sales if (
                search_query_cf in (s.product_name or '').casefold() or
                search_query_cf in (s.customer_name or '').casefold() or
                search_query_cf in (s.customer_email or '').casefold()
            )]
        
        for sale in db_sales:
            sale_dict = sale.to_dict()
            try:
                sale_dict['sale_date'] = sale.sale_date
            except Exception:
                pass
            sale_dict['source'] = 'database'
            sales_from_db.append(sale_dict)
    except Exception as e:
        messages.error(request, f"Error reading database: {str(e)}")
    
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
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            save_to = request.POST.get('save_to', 'file')
            
            if save_to == 'database':
                try:
                    existing_sale = Sale.objects.filter(
                        product_name=form.cleaned_data['product_name'],
                        customer_email=form.cleaned_data['customer_email'],
                        sale_date=form.cleaned_data['sale_date']
                    ).first()
                    
                    if existing_sale:
                        messages.warning(request, 'A sale with the same product, customer email, and date already exists in the database.')
                    else:
                        sale = Sale(
                            product_name=form.cleaned_data['product_name'],
                            quantity=form.cleaned_data['quantity'],
                            price=form.cleaned_data['price'],
                            sale_date=form.cleaned_data['sale_date'],
                            customer_name=form.cleaned_data['customer_name'],
                            customer_email=form.cleaned_data['customer_email']
                        )
                        sale.save()
                        messages.success(request, 'Sale successfully added to database.')
                except Exception as e:
                    messages.error(request, f'Error saving to database: {str(e)}')
            else:
                sale_data = {
                    'id': str(uuid.uuid4()),
                    'product_name': form.cleaned_data['product_name'],
                    'quantity': form.cleaned_data['quantity'],
                    'price': float(form.cleaned_data['price']),
                    'sale_date': form.cleaned_data['sale_date'].isoformat(),
                    'customer_name': form.cleaned_data['customer_name'],
                    'customer_email': form.cleaned_data['customer_email']
                }
                
                format_type = request.POST.get('format', 'json')
                
                filename = f"sale_{uuid.uuid4().hex}.{format_type}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                try:
                    if format_type == 'json':
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(sale_data, f, indent=2, ensure_ascii=False)
                    else:
                        root = ET.Element('sale')
                        for key, value in sale_data.items():
                            elem = ET.SubElement(root, key)
                            elem.text = str(value)
                        tree = ET.ElementTree(root)
                        tree.write(filepath, encoding='utf-8', xml_declaration=True)
                    
                    messages.success(request, f'Sale successfully saved to {format_type.upper()} file.')
                except Exception as e:
                    messages.error(request, f'Error saving to file: {str(e)}')
            
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SaleForm()
    
    return render(request, 'sales_data/index.html', {'form': form})

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        filename = uploaded_file.name
        
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename = f"{uuid.uuid4().hex}_{filename}"
        
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        try:
            file_content = uploaded_file.read()
            
            if filename.endswith('.json'):
                json.loads(file_content.decode('utf-8'))
            elif filename.endswith('.xml'):
                ET.fromstring(file_content)
            else:
                messages.error(request, 'Unsupported file format. Please upload JSON or XML files only.')
                return redirect('index')
            
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            messages.success(request, f'File {filename} uploaded successfully.')
        except (json.JSONDecodeError, ET.ParseError) as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            messages.error(request, f'Invalid file format: {str(e)}')
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            messages.error(request, f'Error uploading file: {str(e)}')
    
    return redirect('index')

def download_file(request, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        messages.error(request, 'File not found.')
        return redirect('index')
    
    if not (filename.endswith('.json') or filename.endswith('.xml')):
        messages.error(request, 'Invalid file type.')
        return redirect('index')
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

def delete_file(request, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        messages.success(request, f'File {filename} deleted successfully.')
    else:
        messages.error(request, 'File not found.')
    
    return redirect('index')

def delete_sale(request, sale_id):
    deleted = False
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get('id') == sale_id:
                            os.remove(filepath)
                            deleted = True
                            break
                        elif isinstance(data, list):
                            for i, sale in enumerate(data):
                                if isinstance(sale, dict) and sale.get('id') == sale_id:
                                    data.pop(i)
                                    with open(filepath, 'w', encoding='utf-8') as f_out:
                                        json.dump(data, f_out, indent=2, ensure_ascii=False)
                                    
                                    deleted = True
                                    break
                except (json.JSONDecodeError, IOError):
                    pass
        
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.xml'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    id_elem = root.find('id')
                    if root.tag == 'sale' and id_elem is not None and id_elem.text == sale_id:
                        os.remove(filepath)
                        deleted = True
                    else:
                        for sale_elem in root.findall('sale'):
                            id_elem = sale_elem.find('id')
                            if id_elem is not None and id_elem.text == sale_id:
                                root.remove(sale_elem)
                                tree.write(filepath, encoding='utf-8', xml_declaration=True)
                                deleted = True
                except (ET.ParseError, IOError):
                    pass
    except Exception as e:
        messages.error(request, f'Error deleting sale: {str(e)}')
    
    if deleted:
        messages.success(request, 'Sale deleted successfully.')
    else:
        messages.error(request, 'Sale not found.')
    
    return redirect('index')

def search_sales(request):
    query = request.GET.get('q', '')
    source = request.GET.get('source', 'all')
    query_cf = query.casefold() if query else ''

    results = []

    def matches(item):
        if not query_cf:
            return True
        return (
            query_cf in str(item.get('product_name', '') or '').casefold() or
            query_cf in str(item.get('customer_name', '') or '').casefold() or
            query_cf in str(item.get('customer_email', '') or '').casefold()
        )
    
    def _parse_date(value):
        if not value:
            return value
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
        formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d.%m.%Y %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return value

    if source in ('file', 'all'):
        try:
            for filename in os.listdir(UPLOAD_DIR):
                filepath = os.path.join(UPLOAD_DIR, filename)
                if filename.endswith('.json'):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and matches(item):
                                    item_copy = dict(item)
                                    item_copy['source'] = 'file'
                                    results.append(item_copy)
                        elif isinstance(data, dict):
                            if matches(data):
                                data_copy = dict(data)
                                data_copy['source'] = 'file'
                                results.append(data_copy)
                    except (json.JSONDecodeError, IOError):
                        continue
                elif filename.endswith('.xml'):
                    try:
                        tree = ET.parse(filepath)
                        root = tree.getroot()

                        if root.tag == 'sale':
                            sale_data = {}
                            for child in root:
                                if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                                    sale_data[child.tag] = _parse_date(child.text)
                                else:
                                    sale_data[child.tag] = child.text
                            
                            if 'sale_date' in sale_data and isinstance(sale_data['sale_date'], str):
                                sale_data['sale_date'] = _parse_date(sale_data['sale_date'])
                            
                            if matches(sale_data):
                                sale_data['source'] = 'file'
                                results.append(sale_data)
                        else:
                            for sale_elem in root.findall('sale'):
                                sale_data = {}
                                for child in sale_elem:
                                    if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                                        sale_data[child.tag] = _parse_date(child.text)
                                    else:
                                        sale_data[child.tag] = child.text
                                
                                if 'sale_date' in sale_data and isinstance(sale_data['sale_date'], str):
                                    sale_data['sale_date'] = _parse_date(sale_data['sale_date'])
                                
                                if matches(sale_data):
                                    sale_data['source'] = 'file'
                                    results.append(sale_data)
                    except (ET.ParseError, IOError):
                        continue
        except Exception:
            pass

    if source in ('database', 'all'):
        try:
            db_qs = Sale.objects.all()
            if query_cf:
                db_qs = [s for s in db_qs if (
                    query_cf in (s.product_name or '').casefold() or
                    query_cf in (s.customer_name or '').casefold() or
                    query_cf in (s.customer_email or '').casefold()
                )]

            for s in db_qs:
                d = s.to_dict()
                try:
                    d['sale_date'] = s.sale_date.isoformat()
                except Exception:
                    pass
                d['source'] = 'database'
                results.append(d)
        except Exception:
            pass

    return JsonResponse({'sales': results})

def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    
    if request.method == 'POST':
        form = SaleEditForm(request.POST, instance=sale)
        if form.is_valid():
            existing_sale = Sale.objects.filter(
                product_name=form.cleaned_data['product_name'],
                customer_email=form.cleaned_data['customer_email'],
                sale_date=form.cleaned_data['sale_date']
            ).exclude(id=sale_id).first()
            
            if existing_sale:
                messages.warning(request, 'A sale with the same product, customer email, and date already exists.')
            else:
                form.save()
                messages.success(request, 'Sale updated successfully.')
                return redirect('index')
    else:
        form = SaleEditForm(instance=sale)
    
    return render(request, 'sales_data/edit_sale.html', {'form': form, 'sale': sale})

def delete_db_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    messages.success(request, 'Sale deleted successfully.')
    return redirect('index')

def edit_file_sale(request, sale_id):
    sale_data = None
    sale_file_path = None
    file_format = None
    
    def _parse_date(value):
        if not value:
            return value
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
        formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d.%m.%Y %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return value
    
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(UPLOAD_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and data.get('id') == sale_id:
                        sale_data = data
                        sale_file_path = filepath
                        file_format = 'json'
                        break
                    elif isinstance(data, list):
                        for sale in data:
                            if isinstance(sale, dict) and sale.get('id') == sale_id:
                                sale_data = sale
                                sale_file_path = filepath
                                file_format = 'json'
                                break
                        if sale_data:
                            break
            except (json.JSONDecodeError, IOError):
                pass
    
    if not sale_data:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.xml'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    
                    def xml_to_dict(elem):
                        result = {}
                        for child in elem:
                            result[child.tag] = child.text
                        return result
                    
                    if root.tag == 'sale':
                        data = xml_to_dict(root)
                        if data.get('id') == sale_id:
                            sale_data = data
                            sale_file_path = filepath
                            file_format = 'xml'
                            break
                    else:
                        for sale_elem in root.findall('sale'):
                            data = xml_to_dict(sale_elem)
                            if data.get('id') == sale_id:
                                sale_data = data
                                sale_file_path = filepath
                                file_format = 'xml'
                                break
                        if sale_data:
                            break
                except (ET.ParseError, IOError):
                    pass
    
    if not sale_data or not sale_file_path:
        messages.error(request, 'Sale not found.')
        return redirect('index')
    
    if request.method == 'POST':
        form = FileSaleForm(request.POST)
        if form.is_valid():
            sale_date = form.cleaned_data['sale_date']
            if sale_date.tzinfo is None:
                sale_date = sale_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            
            updated_data = {
                'id': sale_id,
                'product_name': form.cleaned_data['product_name'],
                'quantity': form.cleaned_data['quantity'],
                'price': float(form.cleaned_data['price']),
                'sale_date': sale_date.isoformat(),
                'customer_name': form.cleaned_data['customer_name'],
                'customer_email': form.cleaned_data['customer_email']
            }
            
            try:
                if file_format == 'json':
                    with open(sale_file_path, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                        
                    if isinstance(file_data, dict):
                        file_data = updated_data
                    else:
                        for i, item in enumerate(file_data):
                            if item.get('id') == sale_id:
                                file_data[i] = updated_data
                                break
                    
                    with open(sale_file_path, 'w', encoding='utf-8') as f:
                        json.dump(file_data, f, indent=2, ensure_ascii=False)
                else:
                    tree = ET.parse(sale_file_path)
                    root = tree.getroot()
                    
                    def update_xml_element(elem, data):
                        for key, value in data.items():
                            child = elem.find(key)
                            if child is None:
                                child = ET.SubElement(elem, key)
                            child.text = str(value)
                    
                    if root.tag == 'sale':
                        update_xml_element(root, updated_data)
                    else:
                        for sale_elem in root.findall('sale'):
                            id_elem = sale_elem.find('id')
                            if id_elem is not None and id_elem.text == sale_id:
                                update_xml_element(sale_elem, updated_data)
                                break
                    
                    tree.write(sale_file_path, encoding='utf-8', xml_declaration=True)
                
                messages.success(request, 'Sale updated successfully.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Error updating sale: {str(e)}')
    else:
        if isinstance(sale_data.get('sale_date'), str):
            try:
                date_obj = datetime.fromisoformat(sale_data['sale_date'])
            except ValueError:
                date_obj = _parse_date(sale_data['sale_date'])
            
            sale_data['sale_date'] = date_obj.strftime('%Y-%m-%dT%H:%M')
        
        form = FileSaleForm(initial=sale_data)
    
    return render(request, 'sales_data/edit_file_sale.html', {'form': form, 'sale_id': sale_id})