from django.urls import path
from .views import BudgetInitView

urlpatterns = [
    path('api/budget/init/', BudgetInitView.as_view(), name='budget_init'),
]