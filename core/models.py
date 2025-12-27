from django.db import models
from django.contrib.auth.models import User  # For user association

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    income = models.FloatField()
    rent = models.FloatField(default=0)
    loan_repayment = models.FloatField(default=0)
    insurance = models.FloatField(default=0)
    savings_percentage = models.FloatField()
    disposable_income = models.FloatField()
    savings_goal = models.FloatField()
    allocations = models.JSONField()  # Store dict e.g., {'Groceries': 5000, ...}
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Budget for {self.user.username} - {self.created_at}"

# ... existing Budget model ...

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()  # Description
    amount = models.FloatField()
    source = models.CharField(max_length=50)  # receipt, voice, etc.
    category = models.CharField(max_length=50, blank=True)  # From Module 3
    confidence = models.FloatField(default=0.0)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.user.username}"