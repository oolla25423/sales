import os
import xml.etree.ElementTree as ET
from datetime import datetime

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

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

def test_xml_parsing():
    xml_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.xml')]
    print(f"Found XML files: {xml_files}")
    
    for filename in xml_files:
        filepath = os.path.join(UPLOAD_DIR, filename)
        print(f"\nParsing file: {filename}")
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            print(f"Root tag: {root.tag}")
            
            # Handle both formats:
            # 1. Root is 'sale' with data as children (single sale file)
            # 2. Root contains multiple 'sale' children (multiple sales file)
            if root.tag == 'sale':
                print("Single sale format detected")
                sale_data = {}
                for child in root:
                    if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                        sale_data[child.tag] = _parse_date(child.text)
                    else:
                        sale_data[child.tag] = child.text
                    print(f"  {child.tag}: {child.text}")
                
                print(f"Parsed sale data: {sale_data}")
            else:
                print("Multiple sales format detected")
                for sale_elem in root.findall('sale'):
                    sale_data = {}
                    for child in sale_elem:
                        if child.tag == 'sale_date' or child.tag == 'date' or child.tag == 'created_at':
                            sale_data[child.tag] = _parse_date(child.text)
                        else:
                            sale_data[child.tag] = child.text
                        print(f"  {child.tag}: {child.text}")
                    
                    print(f"Parsed sale data: {sale_data}")
        except ET.ParseError as e:
            print(f"Parse error: {e}")

if __name__ == "__main__":
    test_xml_parsing()