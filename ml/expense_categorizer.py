import os
import pickle
import pandas as pd
import numpy as np
_model = None
_vectorizer = None
_label_encoder = None

def _load_models():
    """Lazy load models only when needed"""
    global _model, _vectorizer, _label_encoder
    
    if _model is not None:
        return 

    # Build absolute path to ml/ folder 
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this file
    ml_dir = os.path.join(current_dir, 'ml') if os.path.basename(current_dir) != 'ml' else current_dir
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

def categorize_expense(description, explain=False):
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

        # Step 3: Get confidence
        confidence = 0.0
        if hasattr(_model, "predict_proba"):
            probabilities = _model.predict_proba(text_vector)[0]
            confidence = round(max(probabilities) * 100, 2)

        result = {
            "category": category,
            "confidence": confidence,
            "explanation": "Predicted using trained ML expense categorization model"
        }

        # Optional: Explainability - Get top features (words) using feature importance
        if explain:
            feature_names = _vectorizer.get_feature_names_out()
            if hasattr(_model, 'feature_importances_'):
                importances = _model.feature_importances_
                top_indices = np.argsort(importances)[-5:]  # Top 5 features
                top_features = [feature_names[i] for i in top_indices if importances[i] > 0]
                result["explanation"] = f"Top contributing words: {', '.join(top_features or ['No significant features'])} (matched to {category})"
            else:
                result["explanation"] = "No feature importance available for this model type."

        return result
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            "category": "Miscellaneous",
            "confidence": 0.0,
            "explanation": "Model prediction failed — fallback used"
        }

def categorize_multiple_expenses(descriptions):
    _load_models() 
    
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
        "",  
        None,  
        "IESCO BILL PAYMENT",
        "school fees"
    ]
    
    for test in test_cases:
        result = categorize_expense(test, explain=True)
        print(f"'{test}' -> {result['category']} (Confidence: {result['confidence']:.1f}%) - {result['explanation']}")
    
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