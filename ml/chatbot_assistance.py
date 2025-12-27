import joblib
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

vectorizer = joblib.load('expense_vectorizer.pkl')  # Reuse for query matching

# Sample responses
responses = {
    'spending': 'Your monthly spending on {category} is {amount}.',
    'savings': 'You can potentially save {amount} by cutting {category}.',
    'tips': 'Tip: Track daily expenses to meet your {goal}% savings goal.'
}

def chatbot_query(user_query, user_data_file='data.csv'):
    df = pd.read_csv(user_data_file)
    user_row = df.iloc[0]  # Simulate user
    
    # Vectorize query
    query_vec = vectorizer.transform([user_query])
    
    # Simple matching (cosine sim to known phrases)
    known_queries = ['how much spent on food', 'savings goal', 'financial tips']
    known_vecs = vectorizer.transform(known_queries)
    sim = cosine_similarity(query_vec, known_vecs)[0]
    best_match = np.argmax(sim)
    
    if best_match == 0:  # Spending
        category = 'Groceries' if 'food' in user_query.lower() else 'Transport'
        amount = user_row[category]
        return responses['spending'].format(category=category, amount=amount)
    elif best_match == 1:  # Savings
        amount = user_row['Potential_Savings_Groceries']
        return responses['savings'].format(amount=amount, category='Groceries')
    else:
        goal = user_row['Desired_Savings_Percentage']
        return responses['tips'].format(goal=goal)

# Example
print(chatbot_query('How much did I spend on food?'))