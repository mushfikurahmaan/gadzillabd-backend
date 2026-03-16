from django.utils.text import slugify
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from config.permissions import IsStaffUser
from .models import Brand, Category, NavbarCategory, Product, ProductImage
from .admin_serializers import (
    AdminBrandSerializer,
    AdminCategorySerializer,
    AdminNavbarCategorySerializer,
    AdminProductImageSerializer,
    AdminProductListSerializer,
    AdminProductSerializer,
)


class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Product.objects.select_related(
        'category', 'sub_category',
    ).prefetch_related('images').all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            return AdminProductListSerializer
        return AdminProductSerializer

    @action(detail=False, methods=['get'], url_path='check-slug')
    def check_slug(self, request):
        """Return { available: true } if no product has the given slug."""
        raw = request.query_params.get('slug', '').strip()
        if not raw:
            return Response({'available': True})
        normalized = slugify(raw)
        if not normalized:
            return Response({'available': True})
        exists = Product.objects.filter(slug=normalized).exists()
        return Response({'available': not exists})


class AdminProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = AdminProductImageSerializer
    queryset = ProductImage.objects.all()


class AdminNavbarCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = AdminNavbarCategorySerializer
    queryset = NavbarCategory.objects.prefetch_related('subcategories').all()


class AdminCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.select_related('navbar_category').all()


class AdminBrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = AdminBrandSerializer
    queryset = Brand.objects.all()
