from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    # If null=True, category is global; if user set, it's user-specific
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Categories"
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    deadline = models.DateField()
    progress = models.FloatField(default=0, editable=False)  # Auto-calculated

    def save(self, *args, **kwargs):
        if self.target_amount > 0:
            self.progress = min((self.current_amount / self.target_amount) * 100, 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_repayment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_percentage = models.FloatField(default=0)
    disposable_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_goal = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add this
    allocations = models.JSONField(default=dict) 
    explanation = models.TextField(blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        fixed = self.rent + self.loan_repayment + self.insurance
        savings = self.income * (self.savings_percentage / 100)
        self.disposable_income = self.income - fixed - savings
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Budget for {self.user.username} - {self.created_at.date()}"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    text = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=50)  # sms, manual, voice, receipt
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    confidence = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.category or 'Uncategorized'} ({self.source})"