from django.urls import path
from .views import BudgetInitView,ExpenseInputView,AnalyticsView,ReportView

urlpatterns = [
    path('api/budget/init/', BudgetInitView.as_view(), name='budget_init'),
    path('api/expenses/input/', ExpenseInputView.as_view(), name='expenses_input'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics'),
    path('api/report/', ReportView.as_view(), name='report'),
]