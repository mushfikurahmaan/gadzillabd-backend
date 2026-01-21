from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Brand, Category, Product
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    CategoryFlatSerializer,
    SubcategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class ProductListView(ListAPIView):
    """List products with optional category, subcategory, brand, and featured filters."""
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category', 'sub_category').prefetch_related('images')
        category = self.request.query_params.get('category')
        subcategory = self.request.query_params.get('subcategory')
        brand = self.request.query_params.get('brand')
        
        if category:
            # Support comma-separated category slugs, e.g. category=gadgets,accessories
            category_slugs = [c.strip() for c in category.split(',') if c.strip()]
            if category_slugs:
                # Filter by main category slug(s)
                qs = qs.filter(category__slug__in=category_slugs)
        
        if subcategory:
            # Filter by subcategory slug
            qs = qs.filter(sub_category__slug=subcategory)
        
        if brand:
            # Support comma-separated brands
            brands = [b.strip() for b in brand.split(',') if b.strip()]
            if brands:
                qs = qs.filter(brand__in=brands)
        
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            qs = qs.filter(is_featured=True)
        
        # Hot deals: badge=sale
        hot_deals = self.request.query_params.get('hot_deals')
        if hot_deals and hot_deals.lower() == 'true':
            qs = qs.filter(badge='sale')
        
        return qs


class ProductDetailView(RetrieveAPIView):
    """Get single product by UUID or slug."""
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.filter(is_active=True).select_related('category', 'sub_category').prefetch_related('images')
    lookup_url_kwarg = 'identifier'

    def get_object(self):
        identifier = self.kwargs.get(self.lookup_url_kwarg)
        qs = self.get_queryset()
        try:
            import uuid

            uuid.UUID(str(identifier))
            return get_object_or_404(qs, id=identifier)
        except Exception:
            return get_object_or_404(qs, slug=identifier)


class ProductRelatedView(ListAPIView):
    """Related products for a given product (same category, excluding self)."""
    serializer_class = ProductListSerializer

    def get_queryset(self):
        identifier = self.kwargs.get('identifier')
        qs = Product.objects.filter(is_active=True)
        try:
            import uuid

            uuid.UUID(str(identifier))
            product = get_object_or_404(qs, id=identifier)
        except Exception:
            product = get_object_or_404(qs, slug=identifier)
        return (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(id=product.id)
            .select_related('category', 'sub_category')
            .prefetch_related('images')[:4]
        )


class CategoryListView(ListAPIView):
    """
    List main categories with their subcategories for navigation.
    Returns only active, top-level categories with nested subcategories.
    """
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children')


class CategoryDetailView(RetrieveAPIView):
    """Get a single category by slug with its subcategories."""
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('children')


class SubcategoryListView(ListAPIView):
    """List subcategories for a given main category slug."""
    serializer_class = SubcategorySerializer
    
    def get_queryset(self):
        parent_slug = self.kwargs.get('parent_slug')
        return Category.objects.filter(
            parent__slug=parent_slug,
            is_active=True
        ).order_by('order', 'name')


class BrandListView(APIView):
    """
    List all unique product brands, optionally filtered by category.
    Returns brand names sorted alphabetically.
    Note: This returns brand names from products, not Brand model instances.
    """
    def get(self, request):
        category_slug = request.query_params.get('category')
        
        qs = Product.objects.filter(is_active=True)
        
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        
        # Get unique brands
        brands = qs.values_list('brand', flat=True).distinct().order_by('brand')
        
        return Response(list(brands))


class BrandShowcaseView(APIView):
    """
    List all active brands for the homepage showcase.
    Can filter by brand_type (accessories, gadgets) using query parameter.
    Returns brands ordered by their order field.
    """
    def get(self, request):
        brand_type = request.query_params.get('type')
        
        qs = Brand.objects.filter(is_active=True)
        
        if brand_type:
            qs = qs.filter(brand_type=brand_type)
        
        serializer = BrandSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class ProductSearchView(ListAPIView):
    """
    Real-time product search endpoint.
    Searches product name, brand, and description fields.
    Returns matching products sorted by relevance.
    """
    serializer_class = ProductListSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Product.objects.none()
        
        qs = Product.objects.filter(is_active=True).select_related(
            'category', 'sub_category'
        ).prefetch_related('images')
        
        # Search in name, brand, and description
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )
        
        # Order by name match first (more relevant), then by name
        return qs.order_by('name')[:10]  # Limit to 10 results for performance
