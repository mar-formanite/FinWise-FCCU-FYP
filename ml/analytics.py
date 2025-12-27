import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_analytics(user_data_file='data.csv', user_id=None):
    df = pd.read_csv(user_data_file)
    # Filter for user if multi-user (simulate with first row)
    user_row = df.iloc[0] if user_id is None else df[df['user_id'] == user_id].iloc[0]
    
    # Spending by category
    categories = ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Miscellaneous']
    spending = user_row[categories].values
    total_spend = np.sum(spending)
    summary = {cat: val for cat, val in zip(categories, spending)}
    
    # Visualization: Pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(spending, labels=categories, autopct='%1.1f%%')
    plt.title('Monthly Spending Breakdown')
    plt.savefig('spending_chart.png')  # For app to display/export
    
    # Trends: Compare actual vs potential savings
    potential_savings = user_row[[f'Potential_Savings_{cat}' for cat in categories]].sum()
    
    return {
        'summary': summary,
        'total_spend': total_spend,
        'potential_savings': potential_savings,
        'chart_path': 'spending_chart.png',
        'insights': f"You could save {potential_savings:.2f} by optimizing categories like Groceries."
    }

# Example
print(generate_analytics())