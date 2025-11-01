from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Partner, LeadStage, Lead, Transaction, Payout

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'wallet_balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['wallet_balance', 'created_at']

@admin.register(LeadStage)
class LeadStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_by', 'created_at']
    list_filter = ['created_at']
    ordering = ['order']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'lead_type', 'partner', 'stage', 'deal_amount', 
                    'commission_percent', 'commission_amount', 'commission_paid', 'created_at']
    list_filter = ['lead_type', 'stage', 'commission_paid', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['commission_amount', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        # If commission is marked as paid, credit to partner wallet
        if obj.commission_paid and obj.lead_type == 'partner' and obj.partner:
            if change:  # Only for updates
                old_obj = Lead.objects.get(pk=obj.pk)
                if not old_obj.commission_paid and obj.commission_paid:
                    # Credit commission to partner wallet
                    obj.partner.wallet_balance += obj.commission_amount
                    obj.partner.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        partner=obj.partner,
                        lead=obj,
                        transaction_type='credit',
                        amount=obj.commission_amount,
                        description=f"Commission from lead: {obj.customer_name}"
                    )
        
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['partner', 'transaction_type', 'amount', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['partner__name', 'description']
    readonly_fields = ['created_at']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['partner', 'amount', 'status', 'requested_at', 'processed_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['partner__name']
    readonly_fields = ['requested_at']
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Payout.objects.get(pk=obj.pk)
            
            # If status changed to completed
            if old_obj.status != 'completed' and obj.status == 'completed':
                # Deduct from partner wallet
                obj.partner.wallet_balance -= obj.amount
                obj.partner.save()
                obj.processed_by = request.user
                obj.processed_at = timezone.now()
                
                # Create transaction record
                Transaction.objects.create(
                    partner=obj.partner,
                    transaction_type='debit',
                    amount=obj.amount,
                    description=f"Payout processed - {obj.remarks or 'Bank transfer'}"
                )
        
        super().save_model(request, obj, form, change)