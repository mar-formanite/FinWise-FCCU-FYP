import os
import pickle
import pandas as pd
import numpy as np

# --- DO NOT LOAD ANYTHING AT MODULE LEVEL ---
_model = None
_vectorizer = None
_label_encoder = None

def _load_models():
    """Lazy load models only when needed"""
    global _model, _vectorizer, _label_encoder
    
    if _model is not None:
        return  # Already loaded

    # Build absolute path to ml/ folder (robust way)
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this file
    ml_dir = os.path.join(current_dir, 'ml') if os.path.basename(current_dir) != 'ml' else current_dir
    # If this file is in root, ml/ is sibling; if in core/, ml/ is sibling of parent

    model_path = os.path.join(ml_dir, 'expense_categorizer_model.pkl')
    vectorizer_path = os.path.join(ml_dir, 'expense_vectorizer.pkl')
    label_encoder_path = os.path.join(ml_dir, 'label_encoder.pkl')

    missing = []
    for path, name in [(model_path, 'model'), (vectorizer_path, 'vectorizer'), (label_encoder_path, 'label_encoder')]:
        if not os.path.exists(path):
            missing.append(f"{name}: {path}")

    if missing:
        raise FileNotFoundError(
            "ML model files not found in ml/ folder:\n" + "\n".join(missing) +
            "\n\nCurrent working dir: " + os.getcwd() +
            "\nLooking in: " + ml_dir +
            "\nPlease ensure you've trained the model first!"
        )

    with open(model_path, 'rb') as f:
        _model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        _vectorizer = pickle.load(f)
    with open(label_encoder_path, 'rb') as f:
        _label_encoder = pickle.load(f)

    print("ML models loaded successfully from ml/")

def categorize_expense(description):
    _load_models()  # Load models only when needed

    # Handle empty / invalid input
    if not description:
        return {
            "category": "Miscellaneous",
            "confidence": 0.0,
            "explanation": "Empty or invalid description"
        }

    description = str(description).strip()

    if len(description) == 0:
        return {
            "category": "Miscellaneous",
            "confidence": 0.0,
            "explanation": "Empty description after cleaning"
        }

    try:
        # Step 1: Vectorize
        text_vector = _vectorizer.transform([description])

        # Step 2: Predict category
        prediction_encoded = _model.predict(text_vector)[0]
        category = _label_encoder.inverse_transform([prediction_encoded])[0]

        # Step 3: Predict confidence
        if hasattr(_model, "predict_proba"):
            probabilities = _model.predict_proba(text_vector)[0]
            confidence = round(max(probabilities) * 100, 2)
        else:
            confidence = 0.0

        return {
            "category": category,
            "confidence": confidence,
            "explanation": "Predicted using trained ML expense categorization model"
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            "category": "Miscellaneous",
            "confidence": 0.0,
            "explanation": "Model prediction failed — fallback used"
        }


def categorize_multiple_expenses(descriptions):
    """
    Categorize multiple expenses at once (more efficient for batch processing).
    
    Args:
        descriptions (list): List of transaction descriptions
    
    Returns:
        list: List of category names
    """
    _load_models()  # Only loads when function is called
    
    if not descriptions:
        return []
    
    # Clean descriptions
    cleaned = [str(d).strip() if d else "" for d in descriptions]
    
    # Vectorize all at once (faster than one-by-one)
    text_vectors = _vectorizer.transform(cleaned)
    
    # Predict all
    predictions_encoded = _model.predict(text_vectors)
    
    # Convert all back to names
    categories = _label_encoder.inverse_transform(predictions_encoded)
    
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