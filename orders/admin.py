from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Phone-based checkout: hide user/email, show phone + delivery area.
    list_display = ['id', 'phone', 'delivery_area', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]

    # Hide fields that aren't used in the manual checkout flow.
    exclude = ('user', 'email')
