from django.urls import path
from .views import  BudgetInitView,ExpenseInputView,AnalyticsView,ReportView,InflationForecastView,InvestmentView,ChatbotView
from django.contrib.auth.views import LogoutView
urlpatterns = [
    #path('login/', login_view, name='login'),
    #path('face-login/', face_login_simulate, name='face_login'),
    #path('dashboard/', dashboard, name='dashboard'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('api/budget/init/', BudgetInitView.as_view(), name='budget_init'),
    path('api/expenses/input/', ExpenseInputView.as_view(), name='expenses_input'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics'),
    path('api/report/', ReportView.as_view(), name='report'),
    path('api/inflation/', InflationForecastView.as_view(), name='inflation'),
    path('api/investment/', InvestmentView.as_view(), name='investment'),
    path('api/chatbot/', ChatbotView.as_view(), name='chatbot'),
]