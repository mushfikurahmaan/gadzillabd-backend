from django.contrib import admin
from .models import Order, OrderItem

from config.admin_site import custom_admin_site


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Remove size from inline; show product name explicitly.
    fields = ('product_name', 'quantity', 'price')
    readonly_fields = ('product_name',)

    @admin.display(description='Product name')
    def product_name(self, obj: OrderItem):
        return getattr(obj.product, 'name', '') or str(obj.product_id)


@admin.register(Order, site=custom_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['product_names', 'shipping_name', 'phone', 'district', 'delivery_area', 'status', 'total', 'created_at']
    list_filter = ['status', 'delivery_area', 'created_at']
    list_editable = ['status']
    inlines = [OrderItemInline]

    exclude = ('user',)

    @admin.display(description='Products')
    def product_names(self, obj: Order):
        # Join first few item names to keep list readable.
        names = [oi.product.name for oi in obj.items.select_related('product').all()]
        if not names:
            return ''
        if len(names) <= 3:
            return ', '.join(names)
        return ', '.join(names[:3]) + f' (+{len(names) - 3} more)'
