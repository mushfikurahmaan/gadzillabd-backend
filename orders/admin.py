from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Remove size from inline; show product name explicitly.
    fields = ('product', 'product_name', 'quantity', 'price')
    readonly_fields = ('product_name',)

    @admin.display(description='Product')
    def product_name(self, obj: OrderItem):
        return getattr(obj.product, 'name', '') or str(obj.product_id)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Phone-based checkout: hide user/email, show phone + delivery area.
    list_display = ['short_id', 'shipping_name', 'phone', 'delivery_area', 'product_names', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]

    # Hide fields that aren't used in the manual checkout flow.
    exclude = ('user', 'email')

    @admin.display(description='Order')
    def short_id(self, obj: Order):
        return str(obj.id)[:8]

    @admin.display(description='Products')
    def product_names(self, obj: Order):
        # Join first few item names to keep list readable.
        names = [oi.product.name for oi in obj.items.select_related('product').all()]
        if not names:
            return ''
        if len(names) <= 3:
            return ', '.join(names)
        return ', '.join(names[:3]) + f' (+{len(names) - 3} more)'
