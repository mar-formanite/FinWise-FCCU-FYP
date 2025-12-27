import pandas as pd
import numpy as np

def initialize_budget(income, fixed_expenses_dict, savings_percentage, user_data_file='data.csv'):
    # Load historical data for allocation insights
    df = pd.read_csv(user_data_file)
    avg_allocations = df[['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Miscellaneous']].mean().to_dict()
    total_avg = sum(avg_allocations.values())
    alloc_ratios = {k: v / total_avg for k, v in avg_allocations.items()}
    
    # Calculate fixed total
    fixed_total = sum(fixed_expenses_dict.values())  # e.g., {'Rent': 10000, 'Loan': 5000, 'Insurance': 2000}
    
    # Savings goal
    savings_goal = income * (savings_percentage / 100)
    
    # Disposable income
    disposable = income - fixed_total - savings_goal
    
    # Suggested allocations
    allocations = {cat: disposable * ratio for cat, ratio in alloc_ratios.items()}
    
    return {
        'disposable_income': disposable,
        'savings_goal': savings_goal,
        'allocations': allocations,
        'explanation': f"Based on average spending patterns from dataset. Total fixed: {fixed_total}. Aim to stay under allocations to meet {savings_percentage}% savings."
    }

# Example: From data.csv first row
df = pd.read_csv('data.csv')
income = df['Income'].iloc[0]
fixed = {'Rent': df['Rent'].iloc[0], 'Loan_Repayment': df['Loan_Repayment'].iloc[0], 'Insurance': df['Insurance'].iloc[0]}
savings_pct = df['Desired_Savings_Percentage'].iloc[0]
print(initialize_budget(income, fixed, savings_pct))