from django.contrib import admin
from .models import ContactSubmission

from config.admin_site import custom_admin_site


@admin.register(ContactSubmission, site=custom_admin_site)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'phone', 'email']
