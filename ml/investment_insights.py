# investment_insights.py
import requests

def get_investment_data():
    # Gold price (Rs/gram) from API
    try:
        url = "https://api.metalpriceapi.com/v1/latest?api_key=YOUR_KEY&base=PKR&currencies=XAU"  # Free API key from metalpriceapi.com
        response = requests.get(url)
        data = response.json()
        gold_rate = data['rates']['XAUPKR'] if 'rates' in data else 18000  # Default
    except:
        gold_rate = 18000
    
    # Crypto (Bitcoin in PKR)
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=pkr"
        response = requests.get(url)
        btc_rate = response.json()['bitcoin']['pkr']
    except:
        btc_rate = 18000000  # Default
    
    return gold_rate, btc_rate

def give_investment_advice(savings_rate):
    gold, btc = get_investment_data()
    if savings_rate > 30:
        advice = "Excellent savings! Invest in Meezan Islamic Fund or NBP Stock Fund."
    elif savings_rate > 20:
        advice = "Good savings! Start with HBL Money Market Fund (low risk)."
    else:
        advice = "Focus on saving more. Consider Roshan Digital Account for starters."
    
    advice += f"\nCurrent rates: Gold Rs {gold}/gram | Bitcoin Rs {btc}"
    return advice

# Test for prototype
savings_rate = 25  # Example %
print(give_investment_advice(savings_rate))