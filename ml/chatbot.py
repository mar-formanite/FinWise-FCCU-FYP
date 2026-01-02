from ml.analytics import generate_analytics
from ml.inflation_forecast import forecast_expenses
from ml.investment_insights import investment_insights

def chatbot_query(query, user_id=None):
    query = query.lower().strip()
    
    analytics = generate_analytics(user_id)
    
    if "spend" in query or "spent" in query or "expense" in query:
        if "groceries" in query or "food" in query:
            amount = analytics['summary']['Groceries']
            return f"You spent Rs {amount:.2f} on Groceries this month."
        elif "transport" in query:
            amount = analytics['summary']['Transport']
            return f"You spent Rs {amount:.2f} on Transport this month."
        else:
            total = analytics['total_spend']
            return f"Your total spending this month is Rs {total:.2f}."
    
    if "savings" in query or "save" in query:
        savings = analytics['potential_savings']
        return f"You could potentially save Rs {savings:.2f} by optimizing your spending!"
    
    if "inflation" in query or "future" in query or "next year" in query:
        sample_spending = analytics['summary']
        forecast = forecast_expenses(sample_spending)
        return f"With current inflation trends, your expenses may rise by {forecast['increase_percent']}%. Total spending could be Rs {forecast['forecast_total']:.2f} in 12 months."
    
    if "investment" in query or "invest" in query:
        savings = analytics['potential_savings']
        insights = investment_insights(savings)
        return insights['advice']
    
    if "tip" in query or "advice" in query:
        return "Tip: Track daily expenses and aim to keep discretionary spending (eating out, entertainment) under 20% of your budget."
    
    return "I'm your FinWise assistant! Ask me about spending, savings, inflation, investments, or tips."

# Test
if __name__ == "__main__":
    print(chatbot_query("How much did I spend on food?"))
    print(chatbot_query("What is my potential savings?"))
    print(chatbot_query("What about inflation next year?"))
    print(chatbot_query("Give me an investment tip"))