from django.contrib import admin
from django import forms
from .models import Brand, Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductAdminForm(forms.ModelForm):
    """Custom form to filter subcategory choices based on selected category."""
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show main categories (parent=null) for the category field
        self.fields['category'].queryset = Category.objects.filter(parent__isnull=True, is_active=True)
        # Show all subcategories initially; will be filtered by JavaScript in admin
        self.fields['sub_category'].queryset = Category.objects.filter(parent__isnull=False, is_active=True)
        self.fields['sub_category'].required = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'brand', 'get_category', 'get_sub_category', 'price', 'stock', 'badge', 'is_featured', 'is_active']
    list_editable = ['stock']
    list_filter = ['category', 'sub_category', 'badge', 'is_featured', 'is_active']
    search_fields = ['name', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    autocomplete_fields = ['category', 'sub_category']
    fieldsets = (
        (None, {
            'fields': ('name', 'brand', 'slug', 'category', 'sub_category')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'badge')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Additional Information', {
            'fields': ('description', 'stock', 'is_featured', 'is_active')
        }),
    )
    change_form_template = 'admin/products/product/change_form.html'

    def get_category(self, obj):
        return obj.category.name if obj.category else '-'
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'category__name'

    def get_sub_category(self, obj):
        return obj.sub_category.name if obj.sub_category else '-'
    get_sub_category.short_description = 'Subcategory'
    get_sub_category.admin_order_field = 'sub_category__name'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'product_count']
    list_filter = ['parent', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['parent__name', 'order', 'name']

    def product_count(self, obj):
        """Count products in this category (as main or subcategory)."""
        main_count = obj.products.count()
        sub_count = obj.subcategory_products.count()
        if obj.parent is None:
            return f"{main_count} products"
        return f"{sub_count} products"
    product_count.short_description = 'Products'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand_type', 'order', 'is_active', 'redirect_url_preview', 'created_at']
    list_filter = ['brand_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['brand_type', 'order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'image')
        }),
        ('Configuration', {
            'fields': ('brand_type', 'redirect_url', 'order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def redirect_url_preview(self, obj):
        """Show a shortened version of the redirect URL."""
        url = obj.redirect_url
        if len(url) > 40:
            return f"{url[:40]}..."
        return url
    redirect_url_preview.short_description = 'Redirect URL'
