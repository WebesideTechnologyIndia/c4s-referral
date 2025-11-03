from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

from django.db import models
from django.contrib.auth.models import User

class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('sales', 'Sales Executive'),
        ('support', 'Support Executive'),
        ('manager', 'Manager'),
        ('coordinator', 'Coordinator'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    
    # Additional Details
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

class Partner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    # Company/Business Details
    company_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # KYC Documents
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Bank Details
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    account_holder_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Referral code for partner
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track who registered this partner
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registered_partners')
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']



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
    LEAD_TYPE_CHOICES = [
        ('admin', 'Admin Lead'),
        ('partner_own', 'Partner Own Lead'),
        ('partner_referral', 'Partner Referral'),
    ]
    assigned_team_member = models.ForeignKey(
        'TeamMember', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_leads'
    )
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES, default='partner_own')
    stage = models.ForeignKey(LeadStage, on_delete=models.SET_NULL, null=True, blank=True)
    
    deal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_paid = models.BooleanField(default=False)
    
    additional_notes = models.TextField(blank=True, null=True)

    
    # ✅ YE NAYA FIELD ADD KARO
    assigned_to_admin = models.BooleanField(default=False)
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate commission amount
        if self.deal_amount and self.commission_percent:
            self.commission_amount = (self.deal_amount * self.commission_percent) / 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_name} - {self.partner.name if self.partner else 'Admin'}"
    
    class Meta:
        ordering = ['-created_at']

class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    team_member = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField()
    
    # ✅ Follow-up Date
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note for {self.lead.customer_name} - {self.created_at.strftime('%d %b %Y')}"
    
    class Meta:
        ordering = ['-created_at']
        
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
    

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField

class Blog(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    content = RichTextField()  # CKEditor field
    
    # Featured image
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    
    # Order and status
    order_number = models.IntegerField(default=0, help_text="Lower number = Higher priority")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # Meta fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    meta_description = models.TextField(max_length=160, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order_number', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

