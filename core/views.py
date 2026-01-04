from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Budget,Transaction
from .serializers import BudgetSerializer,TransactionSerializer
import pandas as pd  
from ml.multi_modal_input import process_inputs 
from django.contrib.auth.models import User
from ml.analytics import generate_analytics, generate_pdf_report
from django.http import FileResponse
from ml.inflation_forecast import forecast_expenses
from ml.investment_insights import investment_insights
from ml.chatbot import chatbot_query
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
def initialize_budget(income, fixed_expenses_dict, savings_percentage, user_data_file='ml/data.csv'): 
    df = pd.read_csv(user_data_file)
    avg_allocations = df[['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Miscellaneous']].mean().to_dict()
    total_avg = sum(avg_allocations.values())
    alloc_ratios = {k: v / total_avg for k, v in avg_allocations.items()}
    
    fixed_total = sum(fixed_expenses_dict.values())
    savings_goal = income * (savings_percentage / 100)
    disposable = income - fixed_total - savings_goal
    allocations = {cat: disposable * ratio for cat, ratio in alloc_ratios.items()}
    
    return {
        'disposable_income': disposable,
        'savings_goal': savings_goal,
        'allocations': allocations,
        'explanation': f"Based on average spending patterns from dataset. Total fixed: {fixed_total}. Aim to stay under allocations to meet {savings_percentage}% savings."
    }

class BudgetInitView(APIView):
    def post(self, request):
        # Assume authenticated user (add auth later)
        user = User.objects.first()  # Use superuser for testing
        if not user:
            return Response({"error": "No users — run createsuperuser"}, status=400)
        
        # Get inputs from Flutter POST
        income = float(request.data.get('income', 0))
        rent = float(request.data.get('rent', 0))
        loan_repayment = float(request.data.get('loan_repayment', 0))
        insurance = float(request.data.get('insurance', 0))
        savings_percentage = float(request.data.get('savings_percentage', 0))
        
        fixed_expenses = {'Rent': rent, 'Loan_Repayment': loan_repayment, 'Insurance': insurance}
        
        # Run initialization
        budget_data = initialize_budget(income, fixed_expenses, savings_percentage)
        
        # Save to DB
        budget = Budget(
            user=user,
            income=income,
            rent=rent,
            loan_repayment=loan_repayment,
            insurance=insurance,
            savings_percentage=savings_percentage,
            disposable_income=budget_data['disposable_income'],
            savings_goal=budget_data['savings_goal'],
            allocations=budget_data['allocations'],
            explanation=budget_data['explanation']
        )
        budget.save()
        
        serializer = BudgetSerializer(budget)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class ExpenseInputView(APIView):
    def post(self, request):
        user = User.objects.first()
        if not user:
            return Response({"error": "No users found - create one with createsuperuser"}, status=400)# Assume auth
        input_data = request.data  # e.g., {'type': 'receipt_image', 'data': 'uploaded_image_path_or_text'}
        
        txs = process_inputs(input_data)
        
        saved_txs = []
        for tx in txs:
            if 'error' in tx:
                return Response({'error': tx['error']}, status=status.HTTP_400_BAD_REQUEST)
            transaction = Transaction(
                user=user,
                text=tx['text'],
                amount=tx['amount'],
                source=tx['source'],
                category=tx.get('category_obj'),
                confidence=tx.get('confidence', 0.0),
                explanation=tx.get('explanation', '')
            )
            transaction.save()
            saved_txs.append(TransactionSerializer(transaction).data)
        
        return Response(saved_txs, status=status.HTTP_201_CREATED)

class AnalyticsView(APIView):
    def get(self, request):
        user_id = request.user.id if request.user.is_authenticated else None
        result = generate_analytics(user_id)
        return Response(result)

class ReportView(APIView):
    def get(self, request):
        analytics = generate_analytics(request.user.id if request.user.is_authenticated else None)
        pdf_path = generate_pdf_report(analytics)
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='spending_report.pdf')
    
class InflationForecastView(APIView):
    def get(self, request):
        # Use sample or from DB/user spending (for prototype, use sample)
        sample_spending = {"Groceries": 6659, "Transport": 2637, "Eating_Out": 1652,
                           "Entertainment": 1536, "Utilities": 2912, "Healthcare": 1547,
                           "Education": 0, "Miscellaneous": 832}
        result = forecast_expenses(sample_spending)
        return Response(result)
    
class InvestmentView(APIView):
    def get(self, request):
        savings = 15000  # Sample — later from user budget/DB
        result = investment_insights(savings)
        return Response(result)

class ChatbotView(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        user_id = request.user.id if request.user.is_authenticated else None
        response = chatbot_query(query, user_id)
        return Response({"response": response})
