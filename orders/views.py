from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from cart.views import get_or_create_cart

from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderCreateView(CreateAPIView):
    """Create order from current cart."""
    serializer_class = OrderCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cart = get_or_create_cart(request)
        items = list(cart.items.select_related('product'))
        if not items:
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get products with locked rows for atomic stock updates
        from products.models import Product
        product_ids = [ci.product_id for ci in items]
        locked_products = {
            p.id: p for p in Product.objects.filter(
                id__in=product_ids
            ).select_for_update()
        }
        
        # Check stock availability
        stock_errors = []
        for ci in items:
            product = locked_products.get(ci.product_id)
            if not product:
                stock_errors.append(f"Product {ci.product.name} not found.")
                continue
            if product.stock < ci.quantity:
                stock_errors.append(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock}, Requested: {ci.quantity}"
                )
        
        if stock_errors:
            return Response(
                {'detail': 'Stock validation failed.', 'errors': stock_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order and reduce stock
        total = Decimal('0.00')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=ser.validated_data['email'],
            shipping_name=ser.validated_data['shipping_name'],
            shipping_address=ser.validated_data['shipping_address'],
        )
        for ci in items:
            product = locked_products[ci.product_id]
            price = product.price
            OrderItem.objects.create(
                order=order, product=product, quantity=ci.quantity,
                size=ci.size or '', price=price
            )
            # Reduce stock atomically
            product.stock -= ci.quantity
            product.save(update_fields=['stock'])
            total += price * ci.quantity
        order.total = total
        order.save(update_fields=['total'])
        cart.items.all().delete()
        return Response(
            OrderSerializer(instance=order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class OrderListView(ListAPIView):
    """List orders for the authenticated user."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product', 'items__product__images'
        )


class OrderDetailView(RetrieveAPIView):
    """Get order by id (for track-order). Allow by id + email for guests."""
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('items__product', 'items__product__images')

    def get_object(self):
        order_id = self.kwargs.get('id')
        order = self.get_queryset().filter(id=order_id).first()
        if not order:
            raise NotFound()
        if order.user_id and (not self.request.user.is_authenticated or order.user_id != self.request.user.id):
            raise NotFound()
        if not order.user_id:
            email = self.request.query_params.get('email', '').strip().lower()
            if not email or order.email.lower() != email:
                raise NotFound()
        return order
