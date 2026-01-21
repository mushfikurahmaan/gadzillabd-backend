from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import WishlistItem
from .serializers import WishlistAddSerializer, WishlistItemSerializer


class WishlistListView(ListAPIView):
    """List current user's wishlist items."""
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related(
            'product'
        ).prefetch_related('product__images')


class WishlistAddView(APIView):
    """Add product to wishlist. Idempotent."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = WishlistAddSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        product = Product.objects.get(id=ser.validated_data['product_id'])
        _, created = WishlistItem.objects.get_or_create(
            user=request.user, product=product
        )
        return Response(
            {'status': 'added', 'created': created},
            status=status.HTTP_201_CREATED
        )


class WishlistRemoveView(APIView):
    """Remove product from wishlist."""
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        deleted, _ = WishlistItem.objects.filter(
            user=request.user, product_id=product_id
        ).delete()
        return Response({'status': 'removed', 'deleted': deleted > 0})
