from django.urls import path
from .views import BudgetInitView

urlpatterns = [
    path('api/budget/init/', BudgetInitView.as_view(), name='budget_init'),
    path('api/expenses/input/', ExpenseInputView.as_view(), name='expenses_input'),
]