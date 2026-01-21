from django.conf import settings
from django.db import models

from products.models import Product


class WishlistItem(models.Model):
    """User's wishlist: one row per user+product."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'product']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product.name}"
