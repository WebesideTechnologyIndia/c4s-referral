from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in admin (database management)
    path('django-admin/', admin.site.urls),  # Changed from 'admin/' to 'django-admin/'
    
    # Your referral system app (custom admin panel with sidebar)
    path('', include('referal_system.urls')),  # This includes all your custom URLs
]