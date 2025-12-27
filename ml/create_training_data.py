import pandas as pd
import random
import numpy as np

# Your Pakistani merchant examples
merchants = {
    'Groceries': [
        'Carrefour Islamabad', 'Imtiaz Super Market', 'Metro Cash & Carry',
        'Al-Fatah Supermarket', 'Save Mart', 'Local Kiryana Store',
        'Greenvalley Hypermarket', 'Shams Store', 'Bio-Organic & Wholefoods',
        'Islamabad Cash & Carry'
    ],
    'Transport': [
        'Careem Ride', 'Uber Islamabad', 'InDriver', 'Shell Petrol Station',
        'PSO Fuel Pump', 'Total Parco', 'SNGPL Transport', 'Local Rickshaw',
        'Punjab Transport', 'Islamabad Metro Bus'
    ],
    'Eating_Out': [
        'McDonald\'s Islamabad', 'KFC Pakistan', 'OPTP', 'Foodpanda Order',
        'Chaaye Khana', 'United King', 'Salt\'n Pepper', 'Pizza Hut Pakistan',
        'Bundoo Khan', 'Bar.B.Q Tonight'
    ],
    'Utilities': [
        'IESCO', 'SNGPL', 'WASA Islamabad', 'PTCL', 'K-Electric',
        'Sui Southern Gas', 'Electricity Bill', 'Gas Bill'
    ],
    'Healthcare': [
        'Shifa International', 'Islamabad Diagnostic', 'Aga Khan Pharmacy',
        'Chughtai Lab', 'Medicare Hospital', 'Fazal Din Hospital',
        'Local Clinic', 'Medical Store'
    ],
    'Entertainment': [
        'Cinepax Islamabad', 'Nueplex Cinemas', 'Alhamra Arts',
        'Event Ticket', 'Amusement Park', 'Recreation Center'
    ],
    'Education': [
        'COMSATS', 'NUST', 'International Grammar School',
        'Tuition Fees', 'Saeed Book Bank', 'Coaching Center'
    ],
    'Miscellaneous': [
        'Edhi Foundation', 'Saylani Welfare', 'JazzCash', 'Easypaisa',
        'Jubilee Life Insurance', 'EFU Life', 'Bank Loan'
    ]
}

# Generic items commonly found on receipts (Pakistani context)
generic_items = {
    'Groceries': [
        'Milk', 'Bread', 'Rice', 'Atta', 'Dal', 'Sugar', 'Tea', 'Eggs',
        'Chicken', 'Beef', 'Mutton', 'Vegetables', 'Fruits', 'Yogurt',
        'Butter', 'Cheese', 'Naan', 'Roti', 'Basmati Rice', 'Cooking Oil'
    ],
    'Transport': [
        'Petrol', 'Diesel', 'CNG', 'Taxi Fare', 'Bus Ticket', 'Rickshaw',
        'Parking Fee', 'Toll Plaza', 'Motor Oil', 'Car Wash'
    ],
    'Eating_Out': [
        'Pizza', 'Burger', 'Biryani', 'Karahi', 'Tikka', 'Kebab', 'Naan',
        'Lassi', 'Tea', 'Coffee', 'Sandwich', 'Shawarma', 'Roll Paratha'
    ],
    'Healthcare': [
        'Medicine', 'Panadol', 'Antibiotics', 'Consultation', 'Lab Test',
        'X-Ray', 'Blood Test', 'Vaccine', 'Medical Checkup', 'Pharmacy'
    ],
    'Education': [
        'Books', 'Notebooks', 'Pens', 'School Fees', 'Uniform', 'Stationery',
        'Course Fee', 'Registration', 'Admission', 'Exam Fee'
    ]
}

def create_variations(text):
    """Create realistic variations of transaction descriptions"""
    variations = []
    
    # Original
    variations.append(text)
    
    # Uppercase
    variations.append(text.upper())
    
    # Lowercase
    variations.append(text.lower())
    
    # Abbreviated (first word + ISB/ISL for Islamabad)
    if 'Islamabad' in text:
        variations.append(text.replace('Islamabad', 'ISB'))
        variations.append(text.replace('Islamabad', 'ISL'))
    
    # Remove spaces sometimes (like credit card statements)
    if len(text.split()) > 1:
        variations.append(text.replace(' ', ''))
    
    # Add location markers
    locations = ['F-7', 'F-10', 'G-9', 'Blue Area', 'I-8']
    if random.random() > 0.7:  # 30% chance
        variations.append(f"{text} {random.choice(locations)}")
    
    # Bank statement format (truncated)
    if len(text) > 15:
        variations.append(text[:15] + '...')
    
    # Add transaction IDs (like real statements)
    if random.random() > 0.8:  # 20% chance
        variations.append(f"{text} REF{random.randint(1000,9999)}")
    
    return variations

def generate_amount(category):
    """Generate realistic amounts for each category in PKR"""
    amount_ranges = {
        'Groceries': (100, 15000),
        'Transport': (50, 5000),
        'Eating_Out': (200, 8000),
        'Utilities': (500, 25000),
        'Healthcare': (300, 50000),
        'Entertainment': (500, 10000),
        'Education': (1000, 100000),
        'Miscellaneous': (100, 20000)
    }
    
    min_amt, max_amt = amount_ranges.get(category, (100, 10000))
    # Use log-normal distribution for more realistic amounts
    amount = np.random.lognormal(np.log(min_amt + (max_amt-min_amt)/4), 1)
    return min(max(amount, min_amt), max_amt)

def create_training_data(num_samples=1500):
    """Create comprehensive training dataset"""
    data = []
    
    for category in merchants.keys():
        # Calculate samples per category (balanced dataset)
        samples_per_category = num_samples // len(merchants)
        
        merchant_list = merchants[category]
        item_list = generic_items.get(category, [])
        
        for _ in range(samples_per_category):
            # 60% merchants, 40% generic items
            if random.random() < 0.6 and merchant_list:
                base_text = random.choice(merchant_list)
            elif item_list:
                base_text = random.choice(item_list)
            else:
                base_text = random.choice(merchant_list)
            
            # Get variations
            variations = create_variations(base_text)
            description = random.choice(variations)
            
            # Generate amount
            amount = round(generate_amount(category), 2)
            
            data.append({
                'description': description,
                'amount': amount,
                'category': category
            })
    
    # Shuffle the data
    random.shuffle(data)
    
    return pd.DataFrame(data)

# Generate the training data
print("Generating training data...")
df_training = create_training_data(1500)

# Display statistics
print(f"\nTotal samples generated: {len(df_training)}")
print(f"\nCategory distribution:")
print(df_training['category'].value_counts())

print(f"\nSample data:")
print(df_training.sample(10))

# Save to CSV
df_training.to_csv('transaction_training_data.csv', index=False)
print(f"\nTraining data saved to 'transaction_training_data.csv'")

# Show some interesting variations
print("\nExample variations generated:")
for category in ['Groceries', 'Transport', 'Eating_Out']:
    samples = df_training[df_training['category'] == category].sample(3)
    print(f"\n{category}:")
    for _, row in samples.iterrows():
        print(f"  - {row['description']} : PKR {row['amount']}")