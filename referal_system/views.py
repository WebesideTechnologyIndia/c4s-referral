from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .models import Partner, Lead, LeadStage, Transaction, Payout
from django.utils import timezone

# Partner Login
def partner_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'partner'):
            return redirect('partner_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            elif hasattr(user, 'partner'):
                login(request, user)
                return redirect('partner_dashboard')
            else:
                messages.error(request, 'You are not registered as a partner')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'referal_system/partner_login.html')

# Partner Logout
def partner_logout(request):
    logout(request)
    return redirect('partner_login')

# Partner Dashboard
@login_required
def partner_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    
    total_leads = Lead.objects.filter(partner=partner).count()
    total_commission = Lead.objects.filter(partner=partner, commission_paid=True).aggregate(
        total=Sum('commission_amount'))['total'] or 0
    pending_commission = Lead.objects.filter(partner=partner, commission_paid=False).aggregate(
        total=Sum('commission_amount'))['total'] or 0
    
    recent_leads = Lead.objects.filter(partner=partner).order_by('-created_at')[:10]
    recent_transactions = Transaction.objects.filter(partner=partner).order_by('-created_at')[:10]
    
    context = {
        'partner': partner,
        'total_leads': total_leads,
        'total_commission': total_commission,
        'pending_commission': pending_commission,
        'recent_leads': recent_leads,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'referal_system/partner_dashboard.html', context)

# Partner Add Lead
# Partner Add Lead (UPDATED - Own vs Referral)
@login_required
def partner_add_lead(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    stages = LeadStage.objects.all()
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        stage_id = request.POST.get('stage')
        deal_amount = request.POST.get('deal_amount', 0)
        notes = request.POST.get('notes', '')
        
        # NEW - Lead type select karna hai
        lead_ownership = request.POST.get('lead_ownership')  # 'own' ya 'referral'
        
        stage = LeadStage.objects.get(id=stage_id) if stage_id else None
        
        if lead_ownership == 'own':
            # Partner apne liye lead bana raha hai
            Lead.objects.create(
                lead_type='partner_own',
                partner=partner,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                stage=stage,
                deal_amount=float(deal_amount) if deal_amount else 0,
                notes=notes,
                assigned_to_admin=False,  # Partner khud manage karega
                created_by=request.user
            )
            messages.success(request, 'Own lead added successfully! You can manage this lead.')
        else:
            # Partner referral lead bana raha hai - Admin ko assign
            Lead.objects.create(
                lead_type='partner_referral',
                partner=partner,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                stage=stage,
                deal_amount=float(deal_amount) if deal_amount else 0,
                notes=notes,
                assigned_to_admin=True,  # Admin manage karega
                created_by=request.user
            )
            messages.success(request, 'Referral lead submitted to admin! You will receive commission when closed.')
        
        return redirect('partner_dashboard')
    
    context = {
        'partner': partner,
        'stages': stages,
    }
    
    return render(request, 'referal_system/partner_add_lead.html', context)
# Partner Leads List
# Partner Leads List (UPDATED)
# Partner Leads List
@login_required
def partner_leads(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    leads = Lead.objects.filter(partner=partner).order_by('-created_at')
    stages = LeadStage.objects.all()  # YE LINE ADD HUI
    
    context = {
        'partner': partner,
        'leads': leads,
        'stages': stages,  # YE LINE ADD HUI
    }
    
    return render(request, 'referal_system/partner_leads.html', context)
# Partner Wallet
@login_required
def partner_wallet(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    transactions = Transaction.objects.filter(partner=partner).order_by('-created_at')
    payouts = Payout.objects.filter(partner=partner).order_by('-requested_at')
    
    context = {
        'partner': partner,
        'transactions': transactions,
        'payouts': payouts,
    }
    
    return render(request, 'referal_system/partner_wallet.html', context)

# Partner Request Payout
@login_required
def partner_request_payout(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        bank_details = request.POST.get('bank_details')
        
        if amount > partner.wallet_balance:
            messages.error(request, 'Insufficient balance!')
            return redirect('partner_wallet')
        
        if amount < 100:
            messages.error(request, 'Minimum payout amount is ₹100')
            return redirect('partner_wallet')
        
        Payout.objects.create(
            partner=partner,
            amount=amount,
            bank_details=bank_details,
            status='pending'
        )
        
        messages.success(request, 'Payout request submitted successfully!')
        return redirect('partner_wallet')
    
    context = {
        'partner': partner,
    }
    
    return render(request, 'referal_system/partner_request_payout.html', context)

# ===========================================
# ADMIN VIEWS
# ===========================================

# Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access admin dashboard')
        return redirect('partner_login')
    
    total_partners = Partner.objects.count()
    total_leads = Lead.objects.count()
    admin_leads = Lead.objects.filter(lead_type='admin').count()
    partner_leads = Lead.objects.filter(lead_type='partner').count()
    
    total_commission = Lead.objects.filter(commission_paid=True).aggregate(
        total=Sum('commission_amount'))['total'] or 0
    pending_payouts = Payout.objects.filter(status='pending').count()
    
    recent_leads = Lead.objects.all().order_by('-created_at')[:10]
    recent_payouts = Payout.objects.all().order_by('-requested_at')[:5]
    
    context = {
        'total_partners': total_partners,
        'total_leads': total_leads,
        'admin_leads': admin_leads,
        'partner_leads': partner_leads,
        'total_commission': total_commission,
        'pending_payouts': pending_payouts,
        'recent_leads': recent_leads,
        'recent_payouts': recent_payouts,
    }
    
    return render(request, 'referal_system/admin_dashboard.html', context)

# Admin Partners List
@login_required
def admin_partners(request):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    if request.method == 'POST':
        # Register new partner
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        elif Partner.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            Partner.objects.create(user=user, name=name, email=email, phone=phone)
            messages.success(request, 'Partner registered successfully!')
            return redirect('admin_partners')
    
    partners = Partner.objects.all().order_by('-created_at')
    
    context = {
        'partners': partners,
    }
    
    return render(request, 'referal_system/admin_partners.html', context)

# Admin All Leads
@login_required
def admin_leads(request):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    leads = Lead.objects.all().order_by('-created_at')
    stages = LeadStage.objects.all()
    partners = Partner.objects.filter(is_active=True)
    
    context = {
        'leads': leads,
        'stages': stages,
        'partners': partners,
    }
    
    return render(request, 'referal_system/admin_leads.html', context)

# Admin Update Lead
# Admin Update Lead (Admin sirf referral leads aur admin leads update kar sakta hai)
@login_required
def admin_update_lead(request, lead_id):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Check: Admin sirf admin leads aur partner_referral leads update kar sakta hai
    if lead.lead_type == 'partner_own':
        messages.error(request, 'You cannot update partner own leads. Only partner can manage their own leads.')
        return redirect('admin_leads')
    
    if request.method == 'POST':
        stage_id = request.POST.get('stage')
        deal_amount = request.POST.get('deal_amount', 0)
        commission_percent = request.POST.get('commission_percent', 0)
        commission_paid = request.POST.get('commission_paid') == 'on'
        
        lead.stage = LeadStage.objects.get(id=stage_id) if stage_id else lead.stage
        lead.deal_amount = float(deal_amount) if deal_amount else 0
        lead.commission_percent = float(commission_percent) if commission_percent else 0
        
        # Agar commission paid ho raha hai aur pehle paid nahi tha
        if commission_paid and not lead.commission_paid and lead.partner:
            lead.commission_paid = True
            # Wallet mein credit karo
            lead.partner.wallet_balance += lead.commission_amount
            lead.partner.save()
            
            # Transaction create karo
            Transaction.objects.create(
                partner=lead.partner,
                lead=lead,
                transaction_type='credit',
                amount=lead.commission_amount,
                description=f'Commission for lead: {lead.customer_name}'
            )
            messages.success(request, f'Commission of ₹{lead.commission_amount} credited to {lead.partner.name}')
        
        lead.save()
        messages.success(request, 'Lead updated successfully!')
        return redirect('admin_leads')
    
    return redirect('admin_leads')
# Admin Add Lead
@login_required
def admin_add_lead(request):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    stages = LeadStage.objects.all()
    partners = Partner.objects.filter(is_active=True)
    
    if request.method == 'POST':
        lead_type = request.POST.get('lead_type')
        partner_id = request.POST.get('partner')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        stage_id = request.POST.get('stage')
        deal_amount = request.POST.get('deal_amount', 0)
        commission_percent = request.POST.get('commission_percent', 0)
        
        partner = Partner.objects.get(id=partner_id) if partner_id and lead_type == 'partner' else None
        stage = LeadStage.objects.get(id=stage_id) if stage_id else None
        
        Lead.objects.create(
            lead_type=lead_type,
            partner=partner,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            stage=stage,
            deal_amount=float(deal_amount) if deal_amount else 0,
            commission_percent=float(commission_percent) if commission_percent else 0,
            created_by=request.user
        )
        
        messages.success(request, 'Lead added successfully!')
        return redirect('admin_leads')
    
    context = {
        'stages': stages,
        'partners': partners,
    }
    
    return render(request, 'referal_system/admin_add_lead.html', context)

# Admin Lead Stages
@login_required
def admin_stages(request):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        order = request.POST.get('order', 0)
        
        LeadStage.objects.create(
            name=name,
            order=int(order),
            created_by=request.user
        )
        
        messages.success(request, 'Stage created successfully!')
        return redirect('admin_stages')
    
    stages = LeadStage.objects.all().order_by('order')
    
    context = {
        'stages': stages,
    }
    
    return render(request, 'referal_system/admin_stages.html', context)

# Admin Delete Stage
@login_required
def admin_delete_stage(request, stage_id):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    stage = get_object_or_404(LeadStage, id=stage_id)
    stage.delete()
    messages.success(request, 'Stage deleted successfully!')
    return redirect('admin_stages')

# Admin Payouts
@login_required
def admin_payouts(request):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    payouts = Payout.objects.all().order_by('-requested_at')
    
    context = {
        'payouts': payouts,
    }
    
    return render(request, 'referal_system/admin_payouts.html', context)

# Admin Process Payout
@login_required
def admin_process_payout(request, payout_id):
    if not request.user.is_staff:
        return redirect('partner_login')
    
    payout = get_object_or_404(Payout, id=payout_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            payout.status = 'approved'
            payout.processed_by = request.user
            payout.processed_at = timezone.now()
            payout.remarks = remarks
            payout.save()
            messages.success(request, 'Payout approved!')
            
        elif action == 'complete':
            if payout.status == 'approved':
                payout.status = 'completed'
                payout.processed_by = request.user
                payout.processed_at = timezone.now()
                payout.remarks = remarks
                payout.save()
                
                # Wallet se deduct karo
                payout.partner.wallet_balance -= payout.amount
                payout.partner.save()
                
                # Transaction create karo
                Transaction.objects.create(
                    partner=payout.partner,
                    transaction_type='debit',
                    amount=payout.amount,
                    description=f'Payout processed - {remarks}'
                )
                
                messages.success(request, 'Payout completed and amount deducted from wallet!')
            else:
                messages.error(request, 'Payout must be approved first!')
                
        elif action == 'reject':
            payout.status = 'rejected'
            payout.processed_by = request.user
            payout.processed_at = timezone.now()
            payout.remarks = remarks
            payout.save()
            messages.warning(request, 'Payout rejected!')
    
    return redirect('admin_payouts')


# Partner ke views.py mein ye function add karo

# Partner Update Own Lead Stage (Limited Access)


   # Partner Update Own Lead (Sirf apni own leads update kar sakta hai)
@login_required
def partner_update_lead(request, lead_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    partner = get_object_or_404(Partner, user=request.user)
    
    # Sirf apne own leads update kar sakta hai (referral leads nahi)
    lead = get_object_or_404(Lead, id=lead_id, partner=partner, lead_type='partner_own')
    
    if request.method == 'POST':
        stage_id = request.POST.get('stage')
        deal_amount = request.POST.get('deal_amount')
        notes = request.POST.get('notes', '')
        
        if stage_id:
            lead.stage = LeadStage.objects.get(id=stage_id)
        
        if deal_amount:
            lead.deal_amount = float(deal_amount)
        
        lead.notes = notes
        lead.save()
        
        messages.success(request, 'Lead updated successfully!')
        return redirect('partner_leads')
    
    return redirect('partner_leads')