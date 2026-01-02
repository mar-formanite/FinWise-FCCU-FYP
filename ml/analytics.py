import os
import pandas as pd
import numpy as np  # <-- Added this (was missing)
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_analytics(user_id=None, user_data_file=None):
    # Build absolute path to data.csv in project root
    if user_data_file is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))  # ml/ folder
        project_root = os.path.abspath(os.path.join(current_dir, '..'))  # Go up to FineWise/
        user_data_file = os.path.join(project_root, 'data.csv')
    
    if not os.path.exists(user_data_file):
        raise FileNotFoundError(f"data.csv not found at: {user_data_file}\n"
                                f"Current ml directory: {current_dir}\n"
                                f"Expected project root: {project_root}")

    df = pd.read_csv(user_data_file)
    
    # Select user row — fallback to first row if no match
    if user_id is not None and 'user_id' in df.columns:
        matched = df[df['user_id'] == user_id]
        if len(matched) == 0:
            raise ValueError(f"No user found with user_id = {user_id}")
        user_row = matched.iloc[0]
    else:
        user_row = df.iloc[0]  # Default: first row

    # Spending by category - use only columns that exist in data.csv
    all_possible_categories = ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Utilities', 
                           'Healthcare', 'Education', 'Miscellaneous', 'Rent', 'Loan_Repayment', 
                           'Insurance', 'Shopping', 'Travel', 'Subscriptions', 'Gym/Fitness']

# Filter to only columns that exist in the CSV
    categories = [cat for cat in all_possible_categories if cat in df.columns]

# If no categories found, fallback to all numeric columns (safety)
    if not categories:
       categories = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    print(f"Using categories: {categories}")  # For debugging
    spending = user_row[categories].values
    total_spend = np.sum(spending)
    summary = {cat: float(val) for cat, val in zip(categories, spending)}  # Ensure float

    # Potential savings
    potential_cols = [f'Potential_Savings_{cat}' for cat in categories if f'Potential_Savings_{cat}' in df.columns]
    potential_savings = user_row[potential_cols].sum() if potential_cols else 0.0

    # Chart path — save in project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    chart_path = os.path.join(project_root, 'spending_chart.png')

    # Generate pie chart
    plt.figure(figsize=(9, 7))
    plt.pie(spending, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title('Monthly Spending Breakdown', fontsize=16, pad=20)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=200, bbox_inches='tight')
    plt.close()  # Important: free memory

    # Insights
    top_category = max(summary, key=summary.get)
    insights = (f"You spent a total of Rs {total_spend:.2f}. "
                f"You could save Rs {potential_savings:.2f} by optimizing spending. "
                f"Highest category: {top_category} (Rs {summary[top_category]:.2f}).")

    return {
        'summary': summary,
        'total_spend': float(total_spend),
        'potential_savings': float(potential_savings),
        'chart_path': 'spending_chart.png',  # Relative name for API
        'insights': insights
    }

def generate_pdf_report(analytics_result, pdf_path=None):
    if pdf_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        pdf_path = os.path.join(project_root, 'spending_report.pdf')

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 100, "FinWise Monthly Spending Report")

    # Summary
    c.setFont("Helvetica", 12)
    y = height - 160
    c.drawString(100, y, "Monthly Spending Summary:")
    y -= 30
    for cat, amt in analytics_result['summary'].items():
        c.drawString(120, y, f"• {cat}: Rs {amt:.2f}")
        y -= 25

    # Insights
    y -= 20
    c.drawString(100, y, "Insights:")
    y -= 25
    # Wrap long text
    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(analytics_result['insights'], "Helvetica", 12, width - 200)
    for line in lines:
        c.drawString(120, y, line)
        y -= 20

    # Add chart
    chart_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spending_chart.png')
    if os.path.exists(chart_path):
        c.drawImage(chart_path, 80, y - 320, width=450, height=320, preserveAspectRatio=True)

    c.showPage()
    c.save()
    return pdf_path

# Test locally
if __name__ == "__main__":
    try:
        result = generate_analytics()
        print("Analytics Result:")
        print(result)
        pdf = generate_pdf_report(result)
        print(f"\nPDF Report generated at: {pdf}")
        print("Chart saved as: spending_chart.png")
    except Exception as e:
        print(f"Error: {e}")