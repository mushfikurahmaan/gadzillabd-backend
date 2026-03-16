from django.db import models


class DashboardBranding(models.Model):
    """Singleton model for dashboard sidebar branding (logo, admin name, subtitle, currency)."""

    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    admin_name = models.CharField(max_length=100, default="Gadzilla")
    admin_subtitle = models.CharField(max_length=200, default="Admin dashboard")
    currency_symbol = models.CharField(max_length=10, default="৳", blank=True)

    class Meta:
        verbose_name = "Dashboard branding"
        verbose_name_plural = "Dashboard branding"

    def __str__(self):
        return self.admin_name or "Dashboard branding"
