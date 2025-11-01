from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Partner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class LeadStage(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Lead(models.Model):
    LEAD_TYPE_CHOICES = (
        ('admin', 'Admin Lead'),
        ('partner_own', 'Partner Own Lead'),
        ('partner_referral', 'Partner Referral'),
    )
    
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to_admin = models.BooleanField(default=False)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    stage = models.ForeignKey(LeadStage, on_delete=models.SET_NULL, null=True, blank=True)
    deal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leads')
    
    def save(self, *args, **kwargs):
        if self.deal_amount and self.commission_percent:
            self.commission_amount = (self.deal_amount * self.commission_percent) / 100
        super().save(*args, **kwargs)

        
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.partner.name} - {self.transaction_type} - {self.amount}"

class Payout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bank_details = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.partner.name} - {self.amount} - {self.status}"