import pickle
import pandas as pd
import numpy as np

# Load all necessary components (do this once, outside the function)
print("Loading model components...")

try:
    with open('expense_categorizer_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    with open('expense_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
        
    with open('label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    
    print("Model components loaded successfully!")
except FileNotFoundError as e:
    print(f"Error: Model file not found - {e}")
    print("Please ensure you've trained the model first!")
    exit(1)

def categorize_expense(description, return_confidence=False):
    """
    Categorize a single expense description.
    
    Args:
        description (str): Transaction description like "Carrefour F-10"
        return_confidence (bool): If True, also return confidence score
    
    Returns:
        str or tuple: Category name like "Groceries", 
                     or (category, confidence) if return_confidence=True
    """
    
    # Error handling for invalid inputs
    if not description or description is None:
        return "Miscellaneous"  # Default category for empty/invalid input
    
    # Clean the input
    description = str(description).strip()
    
    if len(description) == 0:
        return "Miscellaneous"
    
    try:
        # Step 1: Convert text to numerical features
        text_vector = vectorizer.transform([description])
        
        # Step 2: Get prediction from model (returns encoded number)
        prediction_encoded = model.predict(text_vector)[0]
        
        # Step 3: Convert number back to category name
        category = label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Optional: Get confidence scores
        if return_confidence:
            probabilities = model.predict_proba(text_vector)[0]
            confidence = max(probabilities) * 100
            return category, confidence
        
        return category
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Miscellaneous"  # Fallback category

def categorize_multiple_expenses(descriptions):
    """
    Categorize multiple expenses at once (more efficient for batch processing).
    
    Args:
        descriptions (list): List of transaction descriptions
    
    Returns:
        list: List of category names
    """
    if not descriptions:
        return []
    
    # Clean descriptions
    cleaned = [str(d).strip() if d else "" for d in descriptions]
    
    # Vectorize all at once (faster than one-by-one)
    text_vectors = vectorizer.transform(cleaned)
    
    # Predict all
    predictions_encoded = model.predict(text_vectors)
    
    # Convert all back to names
    categories = label_encoder.inverse_transform(predictions_encoded)
    
    return list(categories)

# Test the function
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing single predictions:")
    print("="*50)
    
    test_cases = [
        "Carrefour market",
        "Pizza delivery", 
        "Uber trip",
        "Medicine store",
        "KFC order",
        "",  # Empty string test
        None,  # None test
        "IESCO BILL PAYMENT",
        "school fees"
    ]
    
    for test in test_cases:
        result = categorize_expense(test, return_confidence=True)
        if isinstance(result, tuple):
            category, confidence = result
            print(f"'{test}' -> {category} (Confidence: {confidence:.1f}%)")
        else:
            print(f"'{test}' -> {result}")
    
    print("\n" + "="*50)
    print("Testing batch prediction:")
    print("="*50)
    
    batch_test = [
        "Carrefour F-10",
        "Uber ride to airport",
        "McDonald's order"
    ]
    
    results = categorize_multiple_expenses(batch_test)
    for desc, cat in zip(batch_test, results):
        print(f"'{desc}' -> {cat}")