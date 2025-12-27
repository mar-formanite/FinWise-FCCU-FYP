
import cv2
import pytesseract
import re
import pickle
import os

# Load your trained models
print("Loading FinWise AI models...")
with open('ml/expense_categorizer_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('ml/expense_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)
with open('ml/label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)
print("All models loaded!\n")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ai_categorize(description):
    vec = vectorizer.transform([description])
    pred = model.predict(vec)[0]
    category = le.inverse_transform([pred])[0]
    confidence = int(max(model.predict_proba(vec)[0]) * 100)
    return category, confidence


# METHOD 1: OCR FROM RECEIPT
print("\n[1] SCANNING RECEIPT WITH CAMERA / IMAGE (OCR)")
print("-" * 60)

confirmed_from_ocr = []

if os.path.exists("images") and os.listdir("images"):
    img_file = os.listdir("images")[0]
    img_path = os.path.join("images", img_file)
    print(f"Found receipt: {img_file}")
    
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    items = []
    for line in text.split('\n'):
        match = re.search(r'([A-Za-z\s&]+).*?([\d,]+\.?\d*)', line.strip())
        if match:
            desc = match.group(1).strip().title()
            try:
                amt = float(match.group(2).replace(',', ''))
                if amt > 30:
                    items.append({"desc": desc, "amount": amt})
            except:
                pass

    if items:
        print(f"Extracted {len(items)} items from receipt:\n")
        for item in items:
            cat, conf = ai_categorize(item["desc"])
            print(f"{item['desc']:<32} -> {cat:<15} Rs {item['amount']:>8.0f} [{conf}%]")
            ans = input("   Is this correct? (y/n/edit): ").strip().lower()
            if ans == 'n' or ans == 'edit':
                cat = input("   Enter correct category: ").strip().title()
            confirmed_from_ocr.append({"desc": item["desc"], "amount": item["amount"], "category": cat})
        print("\nOCR items confirmed!\n")
    else:
        print("No items found (try clearer receipt)\n")
else:
    print("No image in 'images' folder\n")

# METHOD 2: MANUAL ENTRY (LIKE FUTURE APP)
print("[2] MANUAL EXPENSE ENTRY (Same as mobile app)")
print("-" * 60)
print("Enter your expenses (type 'done' to finish)\n")

manual_entries = []
while True:
    desc = input("Description (e.g. Uber ride, KFC meal): ").strip()
    if desc.lower() == 'done':
        break
    if not desc:
        continue
    try:
        amount = float(input("Amount (PKR): "))
    except:
        print("Invalid amount!\n")
        continue

    cat, conf = ai_categorize(desc)
    print(f"AI thinks: {cat} ({conf}% confident)")
    choice = input("   Confirm? (y/n): ").lower()
    if choice == 'n':
        cat = input("   Enter correct category: ").title()
    
    manual_entries.append({"desc": desc, "amount": amount, "category": cat})
    print(f"Added: {desc} -> {cat} (Rs {amount})\n")

# FINAL SUMMARY
all_items = confirmed_from_ocr + manual_entries

print("\n" + "="*80)
print("                        FINAL MONTHLY SUMMARY")
print("="*80)

total_spent = 0
summary = {}

for item in all_items:
    c = item["category"]
    summary[c] = summary.get(c, 0) + item["amount"]
    total_spent += item["amount"]
    print(f"{item['desc']:<35} -> {c:<15} Rs {item['amount']:>8.0f}")

print("-" * 80)
for cat, amt in summary.items():
    perc = (amt / total_spent) * 100 if total_spent > 0 else 0
    print(f"{cat:<20} : Rs {amt:>10.0f} ({perc:>5.1f}%)")
print("-" * 80)
print(f"{'TOTAL SPENT':<20} : Rs {total_spent:>10.0f}")
print("="*80)

print("\nMILESTONE 4 100% COMPLETE")
print("Module 2: Multi-Modal Input (OCR + Manual Entry) -> DONE")
print("Module 3: AI Categorization + User Confirmation -> DONE")
print("="*80)