import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import pickle

# Step 1: Load your data
print("Loading training data...")
df = pd.read_csv('transaction_training_data.csv')
print(f"Loaded {len(df)} transactions")

# Step 2: Encode categories as numbers
label_encoder = LabelEncoder()
df['category_encoded'] = label_encoder.fit_transform(df['category'])

print(f"Categories mapping:")
for i, category in enumerate(label_encoder.classes_):
    print(f"  {category} -> {i}")

# Step 3: Prepare features
X_text = df['description']
y = df['category_encoded']  # Use encoded categories

# Step 4: Convert text to numbers using TF-IDF
print("\nConverting text to numerical features...")
vectorizer = TfidfVectorizer(
    max_features=500,
    ngram_range=(1, 2),
    lowercase=True
)

X = vectorizer.fit_transform(X_text)
print(f"Created {X.shape[1]} features from text")

# Step 5: Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Step 6: Train XGBoost
print("\nTraining XGBoost model...")
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)

# Step 7: Test the model
print("\nEvaluating model...")
y_pred = model.predict(X_test)

# Convert back to category names for readable results
y_test_names = label_encoder.inverse_transform(y_test)
y_pred_names = label_encoder.inverse_transform(y_pred)

accuracy = accuracy_score(y_test_names, y_pred_names)
print(f"Accuracy: {accuracy:.2%}")

print("\nDetailed Results by Category:")
print(classification_report(y_test_names, y_pred_names))

# Step 8: Save EVERYTHING you need
print("\nSaving model components...")
with open('expense_categorizer_model.pkl', 'wb') as f:
    pickle.dump(model, f)
    
with open('expense_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
    
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
    
print("Model, vectorizer, and label encoder saved!")

# Step 9: Test complete pipeline
print("\n" + "="*50)
print("Testing complete pipeline with new examples:")
test_examples = [
    "Carrefour islamabad",
    "uber ride",
    "KFC order",
    "IESCO bill",
    "medicine pharmacy",
    "foodpanda"
]

for example in test_examples:
    # Transform text → numbers
    example_vector = vectorizer.transform([example])
    # Predict (returns number)
    prediction_encoded = model.predict(example_vector)[0]
    # Convert number → category name
    prediction = label_encoder.inverse_transform([prediction_encoded])[0]
    print(f"'{example}' -> {prediction}")