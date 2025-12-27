# inflation_forecast.py
import requests
import numpy as np

def get_pakistan_inflation_rate():
    # Use API for real-time (or hardcode for prototype)
    try:
        url = "https://api.api-ninjas.com/v1/inflation?country=pakistan"  # Free API (sign up for key)
        headers = {'X-Api-Key': 'YOUR_API_KEY'}  # Get free key from api-ninjas.com
        response = requests.get(url, headers=headers)
        data = response.json()
        rate = data[0]['yearly_rate_pct'] if data else 9.5  # Default 9.5%
    except:
        rate = 9.5  # Default for prototype
    return rate / 100  # As decimal

def forecast_expenses(current_spending, months=12):
    rate = get_pakistan_inflation_rate()
    future = current_spending * ((1 + rate) ** (months / 12))
    return future

# Test for prototype
current = 50000  # Monthly spending
future = forecast_expenses(current)
print(f"Current Rs 50,000/month → Rs {future:,.0f} in 12 months due to inflation")