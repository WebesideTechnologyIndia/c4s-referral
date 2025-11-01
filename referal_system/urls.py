from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # PARTNER URLs
    # ============================================
    path('', views.partner_login, name='partner_login'),
    path('logout/', views.partner_logout, name='partner_logout'),
    path('dashboard/', views.partner_dashboard, name='partner_dashboard'),
    path('add-lead/', views.partner_add_lead, name='partner_add_lead'),
    path('my-leads/', views.partner_leads, name='partner_leads'),
    path('my-leads/<int:lead_id>/update/', views.partner_update_lead, name='partner_update_lead'),

    
    path('wallet/', views.partner_wallet, name='partner_wallet'),
    path('request-payout/', views.partner_request_payout, name='partner_request_payout'),
    
    # ============================================
    # ADMIN URLs - Sabke aage 'admin' prefix hai
    # ============================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/partners/', views.admin_partners, name='admin_partners'),
    path('admin/leads/', views.admin_leads, name='admin_leads'),
    path('admin/leads/<int:lead_id>/update/', views.admin_update_lead, name='admin_update_lead'),
    path('admin/add-lead/', views.admin_add_lead, name='admin_add_lead'),
    path('admin/stages/', views.admin_stages, name='admin_stages'),
    path('admin/stages/<int:stage_id>/delete/', views.admin_delete_stage, name='admin_delete_stage'),
    path('admin/payouts/', views.admin_payouts, name='admin_payouts'),
    path('admin/payouts/<int:payout_id>/process/', views.admin_process_payout, name='admin_process_payout'),
]