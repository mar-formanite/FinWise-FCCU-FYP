import re
import xml.etree.ElementTree as ET
import cv2  # From opencv-python
import pytesseract  # For real OCR
from ml.expense_categorizer import categorize_expense  # Assume from your ml folder (Module 3)
from core.models import Category
# Configure Tesseract path if needed (Windows default: C:\Program Files\Tesseract-OCR\tesseract.exe)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust if different
def get_or_create_category(name):
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={'description': f"Auto-created category for {name}"}  # Default value
    )
    if created:
        print(f"Created new category: {name}")
    return cat
def parse_receipt_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return [{'error': f"Failed to load image: {image_path}"}]
        
        # Preprocess image for better OCR (grayscale, threshold)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # OCR extract text
        text = pytesseract.image_to_string(thresh)
        
        # Split into lines/items
        lines = text.splitlines()
        transactions = []
        for line in lines:
            if line.strip():  # Skip empty
                # Improved regex: Handles Rs.500.00, PKR 100, 2.50 FS, $5.99 N, etc.
                amount_match = re.search(r'(Rs\.?|PKR|Rs|₹|\$)?\s*(\d+\.?\d*)\s*(FS|F|N)?$', line, re.IGNORECASE) or re.search(r'(\d+\.?\d*)\s*(Rs\.?|PKR|Rs|₹|\$)?', line, re.IGNORECASE)
                amount = float(amount_match.group(1) or amount_match.group(2)) if amount_match else 0.0
                desc = re.sub(r'(Rs\.?|PKR|Rs|₹|\$)?\s*\d+\.?\d*\s*(FS|F|N)?', '', line).strip()
                transactions.append({'text': desc, 'amount': amount, 'source': 'receipt'})
        return transactions
    except Exception as e:
        return [{'error': f"OCR failed for {image_path}: {str(e)}"}]

def parse_receipt_annotations(xml_file='annotations.xml'):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        transactions = []
        for image in root.findall('image'):
            image_name = image.get('name')  # e.g., images/0.jpg
            for box in image.findall('box'):
                if box.get('label') in ['item', 'total']:
                    text = box.find('attribute').text if box.find('attribute') is not None else ''
                    amount_match = re.search(r'(Rs\.?|PKR|Rs|₹|\$)?\s*(\d+\.?\d*)\s*(FS|F|N)?', text, re.IGNORECASE)
                    amount = float(amount_match.group(2)) if amount_match else 0.0
                    desc = re.sub(r'(Rs\.?|PKR|Rs|₹|\$)?\s*\d+\.?\d*\s*(FS|F|N)?', '', text).strip()
                    transactions.append({'text': desc, 'amount': amount, 'source': 'receipt_annotation', 'image': image_name})
        return transactions
    except Exception as e:
        return [{'error': f"Failed to parse annotations: {str(e)}"}]

def voice_input_simulation(voice_text):
    if not voice_text:
        return {'error': 'No voice input provided'}
    amount_match = re.search(r'(Rs\.?|PKR|Rs|₹|\$)?\s*(\d+\.?\d*)', voice_text, re.IGNORECASE)
    amount = float(amount_match.group(2)) if amount_match else 0.0
    desc = re.sub(r'(Rs\.?|PKR|Rs|₹|\$)?\s*\d+\.?\d*', '', voice_text).strip()
    return {'text': desc, 'amount': amount, 'source': 'voice'}

def manual_input(text, amount_str):
    try:
        amount_match = re.search(r'(\d+\.?\d*)', amount_str)
        amount = float(amount_match.group(1)) if amount_match else 0.0
        return {'text': text, 'amount': amount, 'source': 'manual'}
    except ValueError:
        return {'error': 'Invalid amount for manual input'}

def sms_sync_simulation(sms_text):
    # Pakistan formats: HBL "A/c XX Debited Rs500.00 on 27-12-25 by UPI Txn ID:XXX Ref Grocery", Ufone "Rs.100 deducted for Transport"
    amount_match = re.search(r'(Rs\.?|PKR|Rs|₹)?\s*(\d+\.?\d*)', sms_text, re.IGNORECASE)
    amount = float(amount_match.group(2)) if amount_match else 0.0
    desc_match = re.search(r'(for|Ref|by)\s*(.+)', sms_text, re.IGNORECASE)
    desc = desc_match.group(2).strip() if desc_match else sms_text
    return {'text': desc, 'amount': amount, 'source': 'sms'}

# Batch process and integrate with transaction management (categorize & return for DB save)
def process_inputs(input_data):
    input_type = input_data.get('type')
    data = input_data.get('data')
    
    if input_type == 'receipt_image':
        txs = parse_receipt_image(data)  # data = 'images/0.jpg'
    elif input_type == 'receipt_annotation':
        txs = parse_receipt_annotations(data)  # data = 'annotations.xml'
    elif input_type == 'voice':
        txs = [voice_input_simulation(data)]
    elif input_type == 'manual':
        text, amount_str = data.split('|') if '|' in data else (data, '0')
        txs = [manual_input(text, amount_str)]
    elif input_type == 'sms':
        txs = [sms_sync_simulation(data)]
    else:
        return [{'error': 'Invalid input type'}]
    
    # Integrate with Module 3: Categorize each
    for tx in txs:
        if 'error' not in tx:
            cat_result = categorize_expense(tx['text'], explain=True)
            category_obj = get_or_create_category(cat_result['category'])
            tx['category_obj'] = category_obj  # Save object for DB
            tx['confidence'] = cat_result['confidence']
            tx['explanation'] = cat_result['explanation']
    
    return txs
'''
# Example testing (run in code_execution if needed)
example_inputs = {
    'type': 'receipt_image',
    'data': 'images/0.jpg'  # Assume one of your receipt images
}
print(process_inputs(example_inputs))
'''