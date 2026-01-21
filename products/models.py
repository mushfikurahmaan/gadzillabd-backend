import uuid
from django.db import models  # type: ignore[import-not-found]

try:
    # Import at module level so tooling resolves it consistently.
    from django.core.exceptions import ValidationError  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    # Fallback for editors/type-checkers when Django isn't in the active interpreter.
    class ValidationError(Exception):
        pass


class Category(models.Model):
    """
    Hierarchical categories for products.
    
    Main categories (parent=null): e.g. Gadgets, Accessories
    Subcategories (parent set): e.g. Audio, Wearables, Chargers, Power Bank
    
    Categories are fully dynamic and can be managed from the admin panel.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Category description for the frontend")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order in navigation")
    is_active = models.BooleanField(default=True, help_text="Whether this category is visible on the site")

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def is_main_category(self):
        """Returns True if this is a top-level category."""
        return self.parent is None

    def get_subcategories(self):
        """Returns all active subcategories for this category."""
        return self.children.filter(is_active=True).order_by('order', 'name')


class Product(models.Model):
    """Product model aligned with frontend Product interface."""

    class Badge(models.TextChoices):
        SALE = 'sale', 'Sale'
        NEW = 'new', 'New'
        HOT = 'hot', 'Hot'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    badge = models.CharField(
        max_length=10, choices=Badge.choices, blank=True, null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        help_text="Main category (e.g., Gadgets, Accessories)"
    )
    sub_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategory_products',
        help_text="Subcategory (e.g., Audio, Chargers, Power Bank)"
    )
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        """
        Ensure sub_category belongs to the selected main category.
        """
        super().clean()

        if self.sub_category and self.category:
            # Subcategory must be a child of the selected main category
            if self.sub_category.parent_id != self.category.id:
                raise ValidationError({
                    'sub_category': f'Subcategory must belong to {self.category.name}.'
                })

    def save(self, *args, **kwargs):
        # Keep model-level validation consistent across admin / scripts.
        self.full_clean()
        return super().save(*args, **kwargs)
    
    @property
    def category_slug(self):
        """Returns the main category slug for URL generation."""
        return self.category.slug if self.category else None
    
    @property
    def sub_category_slug(self):
        """Returns the subcategory slug for URL generation."""
        return self.sub_category.slug if self.sub_category else None


class ProductImage(models.Model):
    """Additional images for product detail gallery."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Brand(models.Model):
    """
    Brand model for showcasing top brands on the homepage.
    Supports image upload and redirect URL for brand cards.
    """

    class BrandType(models.TextChoices):
        ACCESSORIES = 'accessories', 'Accessories'
        GADGETS = 'gadgets', 'Gadgets'

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(
        upload_to='brands/',
        help_text="Brand logo or image to display on the brand card"
    )
    redirect_url = models.URLField(
        max_length=500,
        help_text="URL to redirect users when they click on the brand card"
    )
    brand_type = models.CharField(
        max_length=20,
        choices=BrandType.choices,
        help_text="Determines which section the brand appears in on the homepage"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within the brand type section (lower numbers appear first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this brand is visible on the site"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['brand_type', 'order', 'name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return f"{self.name} ({self.get_brand_type_display()})"
