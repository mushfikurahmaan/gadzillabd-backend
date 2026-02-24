from django.contrib import admin
from .models import WishlistItem

from config.admin_site import custom_admin_site


@admin.register(WishlistItem, site=custom_admin_site)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
