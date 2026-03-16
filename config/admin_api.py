from decimal import Decimal

from django.db.models import Sum, Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from config.permissions import IsStaffUser
from core.models import DashboardBranding
from orders.models import Order
from orders.admin_serializers import AdminOrderListSerializer
from products.models import Product, NavbarCategory, Category, Brand
from contact.models import ContactSubmission
from notifications.models import Notification
from cart.models import Cart
from wishlist.models import WishlistItem


class DashboardStatsView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        order_counts = Order.objects.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status=Order.Status.PENDING)),
            confirmed_count=Count('id', filter=Q(status=Order.Status.CONFIRMED)),
            cancelled_count=Count('id', filter=Q(status=Order.Status.CANCELLED)),
        )
        revenue_agg = Order.objects.exclude(
            status=Order.Status.CANCELLED,
        ).aggregate(revenue=Sum('total'))

        product_stats = Product.objects.aggregate(
            total_count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True)),
            oos_count=Count('id', filter=Q(stock=0, is_active=True)),
        )

        recent_orders = Order.objects.prefetch_related('items__product')[:10]

        return Response({
            'orders': {
                'total': order_counts['total_count'],
                'pending': order_counts['pending_count'],
                'confirmed': order_counts['confirmed_count'],
                'cancelled': order_counts['cancelled_count'],
            },
            'revenue': str(revenue_agg['revenue'] or Decimal('0.00')),
            'products': {
                'total': product_stats['total_count'],
                'active': product_stats['active_count'],
                'out_of_stock': product_stats['oos_count'],
            },
            'categories': NavbarCategory.objects.count(),
            'subcategories': Category.objects.count(),
            'brands': Brand.objects.count(),
            'contacts': ContactSubmission.objects.count(),
            'notifications': Notification.objects.filter(is_active=True).count(),
            # Count only carts that actually have at least one item
            'carts': Cart.objects.filter(items__isnull=False).distinct().count(),
            'wishlist': WishlistItem.objects.count(),
            'recent_orders': AdminOrderListSerializer(recent_orders, many=True).data,
        })


def _get_branding_response(request, instance):
    """Build branding JSON for API response."""
    logo_url = None
    if instance.logo:
        logo_url = request.build_absolute_uri(instance.logo.url)
    return {
        'logo_url': logo_url,
        'admin_name': instance.admin_name or 'Gadzilla',
        'admin_subtitle': instance.admin_subtitle or 'Admin dashboard',
        'currency_symbol': instance.currency_symbol or '৳',
    }


class BrandingView(APIView):
    """GET: return branding. PATCH: update branding (multipart: logo, admin_name, admin_subtitle, currency_symbol)."""
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_instance(self):
        instance = DashboardBranding.objects.first()
        if instance is None:
            instance = DashboardBranding.objects.create(
                admin_name='Gadzilla', admin_subtitle='Admin dashboard'
            )
        return instance

    def get(self, request):
        instance = self._get_instance()
        return Response(_get_branding_response(request, instance))

    def patch(self, request):
        instance = self._get_instance()
        if 'admin_name' in request.data:
            instance.admin_name = request.data.get('admin_name', instance.admin_name) or 'Gadzilla'
        if 'admin_subtitle' in request.data:
            instance.admin_subtitle = request.data.get('admin_subtitle', instance.admin_subtitle) or 'Admin dashboard'
        if 'currency_symbol' in request.data:
            instance.currency_symbol = (request.data.get('currency_symbol') or '৳').strip()[:10]
        logo_file = request.FILES.get('logo')
        if logo_file:
            instance.logo = logo_file
        if request.data.get('clear_logo') in (True, 'true', '1'):
            instance.logo = None
        instance.save()
        return Response(_get_branding_response(request, instance))
