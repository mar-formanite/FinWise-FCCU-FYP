import requests

def get_market_data():
    try:
        # Gold in PKR (from coingecko proxy or hardcode latest)
        gold_url = "https://api.coingecko.com/api/v3/simple/price?ids=gold&vs_currencies=pkr"
        btc_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=pkr"
        gold = requests.get(gold_url).json().get('gold', {}).get('pkr', 22000)  # gram approx
        btc = requests.get(btc_url).json().get('bitcoin', {}).get('pkr', 18000000)
    except:
        gold = 22000  # fallback
        btc = 18000000
    return {"gold_per_gram_pkr": gold, "bitcoin_pkr": btc}

def investment_insights(savings_amount):
    market = get_market_data()
    if savings_amount > 20000:
        advice = "Strong savings! Consider Meezan Gold Fund or NBP Islamic Stock Fund."
    elif savings_amount > 10000:
        advice = "Good start! Try HBL Money Market Fund (low risk)."
    else:
        advice = "Focus on building savings. Start with Roshan Digital Account."
    
    advice += f"\nCurrent rates: Gold ~Rs {market['gold_per_gram_pkr']}/gram | Bitcoin ~Rs {market['bitcoin_pkr']:,}"
    
    return {
        "advice": advice,
        "market_data": market,
        "savings_amount_used": savings_amount
    }

# Test
if __name__ == "__main__":
    print(investment_insights(15000))