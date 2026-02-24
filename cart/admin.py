from django.contrib import admin
from .models import Cart, CartItem

from config.admin_site import custom_admin_site


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart, site=custom_admin_site)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'updated_at']
    list_filter = ['updated_at']
    inlines = [CartItemInline]
