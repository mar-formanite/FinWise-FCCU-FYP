import requests
import os

def get_pakistan_inflation_rate():
    # Latest from searches (Dec 2025: 5.6%, 2026 forecast ~6%)
    current_rate = 5.6  # Dec 2025 actual
    forecast_2026 = 6.0  # Average forecast for FY26
    return {"current": current_rate, "forecast_2026": forecast_2026}

def forecast_expenses(current_spending_dict, months=12):
    rates = get_pakistan_inflation_rate()
    forecast_rate = rates["forecast_2026"] / 100  # Decimal
    
    # Category-specific multipliers (food inflates more)
    multipliers = {
        'Groceries': 1.3, 'Eating_Out': 1.2, 'Transport': 1.1,
        'Utilities': 1.15, 'Healthcare': 1.1, 'default': 1.0
    }
    
    forecasted = {}
    for cat, amount in current_spending_dict.items():
        mult = multipliers.get(cat, multipliers['default'])
        future = amount * ((1 + forecast_rate * mult) ** (months / 12))
        forecasted[cat] = round(future, 2)
    
    total_current = sum(current_spending_dict.values())
    total_future = sum(forecasted.values())
    
    return {
        "current_total": round(total_current, 2),
        "forecast_total": round(total_future, 2),
        "increase_percent": round(((total_future - total_current) / total_current) * 100, 1),
        "forecasted_spending": forecasted,
        "inflation_info": f"Based on Dec 2025 rate {rates['current']}% and 2026 forecast ~{rates['forecast_2026']}%. Food categories adjusted higher."
    }

# Test
if __name__ == "__main__":
    sample_spending = {
        "Groceries": 6659, "Transport": 2637, "Eating_Out": 1652,
        "Entertainment": 1536, "Utilities": 2912, "Healthcare": 1547,
        "Education": 0, "Miscellaneous": 832
    }
    result = forecast_expenses(sample_spending)
    print(result)