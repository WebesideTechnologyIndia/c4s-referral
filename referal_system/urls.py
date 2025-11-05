from django.urls import path
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # ============================================
    # PARTNER URLs
    # ============================================
    path("", views.partner_login, name="partner_login"),
    path("logout/", views.partner_logout, name="partner_logout"),
    path("dashboard/", views.partner_dashboard, name="partner_dashboard"),
    path("add-lead/", views.partner_add_lead, name="partner_add_lead"),
    path("my-leads/", views.partner_leads, name="partner_leads"),
    path(
        "my-leads/<int:lead_id>/update/",
        views.partner_update_lead,
        name="partner_update_lead",
    ),
    path("wallet/", views.partner_wallet, name="partner_wallet"),
    path(
        "request-payout/", views.partner_request_payout, name="partner_request_payout"
    ),
    # ============================================
    # ADMIN URLs - Sabke aage 'admin' prefix hai
    # ============================================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/partners/", views.admin_partners, name="admin_partners"),
    path(
        "admin/partners/edit/<int:partner_id>/",
        views.admin_edit_partner,
        name="admin_edit_partner",
    ),
    path(
        "admin/partners/delete/<int:partner_id>/",
        views.admin_delete_partner,
        name="admin_delete_partner",
    ),
    path(
        "admin/partners/toggle-status/<int:partner_id>/",
        views.admin_toggle_partner_status,
        name="admin_toggle_partner_status",
    ),
    path("partner/register/", views.partner_register, name="partner_register"),
    path("admin/leads/", views.admin_leads, name="admin_leads"),
    path(
        "admin/leads/<int:lead_id>/update/",
        views.admin_update_lead,
        name="admin_update_lead",
    ),

        path('partner/leads/assign-to-admin/<int:lead_id>/', views.partner_assign_lead_to_admin, name='partner_assign_lead_to_admin'),

    path("admin/add-lead/", views.admin_add_lead, name="admin_add_lead"),
    path("admin/stages/", views.admin_stages, name="admin_stages"),
    path(
        "admin/stages/<int:stage_id>/delete/",
        views.admin_delete_stage,
        name="admin_delete_stage",
    ),
        path('admin/stages/edit/<int:stage_id>/', views.admin_edit_stage, name='admin_edit_stage'),

    path("admin/payouts/", views.admin_payouts, name="admin_payouts"),
    path(
        "admin/payouts/<int:payout_id>/process/",
        views.admin_process_payout,
        name="admin_process_payout",
    ),
        path('partner/leads/delete/<int:lead_id>/', views.partner_delete_lead, name='partner_delete_lead'),  # ✅ NEW
    path('admin/leads/delete/<int:lead_id>/', views.admin_delete_lead, name='admin_delete_lead'),  # ✅ NEW


    path('admin/blogs/', views.admin_blogs, name='admin_blogs'),
    path('admin/blogs/add/', views.admin_add_blog, name='admin_add_blog'),
    path('admin/blogs/edit/<int:blog_id>/', views.admin_edit_blog, name='admin_edit_blog'),
    path('admin/blogs/delete/<int:blog_id>/', views.admin_delete_blog, name='admin_delete_blog'),
    path('admin/blogs/toggle-status/<int:blog_id>/', views.admin_toggle_blog_status, name='admin_toggle_blog_status'),
    
    # Partner Blog URLs
    path('partner/blogs/', views.partner_blogs, name='partner_blogs'),
    path('partner/blogs/<int:blog_id>/', views.partner_blog_detail, name='partner_blog_detail'),


      path('admin/team-members/', views.admin_team_members, name='admin_team_members'),
    path('admin/team-members/edit/<int:member_id>/', views.admin_edit_team_member, name='admin_edit_team_member'),
    path('admin/team-members/delete/<int:member_id>/', views.admin_delete_team_member, name='admin_delete_team_member'),
    path('admin/team-members/toggle-status/<int:member_id>/', views.admin_toggle_team_member_status, name='admin_toggle_team_member_status'),
    
    # Lead Assignment & Notes
    path('admin/leads/<int:lead_id>/assign-team/', views.admin_assign_team_member, name='admin_assign_team_member'),
    path('admin/leads/<int:lead_id>/add-note/', views.admin_add_lead_note, name='admin_add_lead_note'),
    path('admin/leads/<int:lead_id>/detail/', views.admin_lead_detail, name='admin_lead_detail'),
    

    path('team/dashboard/', views.team_dashboard, name='team_dashboard'),
    path('team/my-leads/', views.team_my_leads, name='team_my_leads'),
    path('team/leads/<int:lead_id>/', views.team_lead_detail, name='team_lead_detail'),
    path('team/leads/<int:lead_id>/update/', views.team_update_lead, name='team_update_lead'),
    path('team/leads/<int:lead_id>/add-note/', views.team_add_note, name='team_add_note'),
    path('team/notes/<int:note_id>/complete/', views.team_mark_followup_complete, name='team_mark_followup_complete'),
    path('team/followup-calendar/', views.team_followup_calendar, name='team_followup_calendar'),
    path('leads/bulk-upload/', views.admin_bulk_upload_leads, name='admin_bulk_upload_leads'),
path('leads/download-sample/', views.download_sample_excel, name='download_sample_excel'),

# Partner Bulk Upload
path('partner/leads/bulk-upload/', views.partner_bulk_upload_leads, name='partner_bulk_upload_leads'),
path('partner/leads/download-sample/', views.partner_download_sample_excel, name='partner_download_sample_excel'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)