from rest_framework import serializers

from .models import Brand, Category, Product, ProductImage


def _image_url(img, request):
    if not img:
        return None
    return request.build_absolute_uri(img.url) if request else img.url


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'order']

    def get_url(self, obj):
        return _image_url(obj.image, self.context.get('request'))


class ProductListSerializer(serializers.ModelSerializer):
    """For list views: matches frontend Product shape."""
    id = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField()
    originalPrice = serializers.DecimalField(
        source='original_price', max_digits=10, decimal_places=2,
        read_only=True, allow_null=True
    )
    # Return category slug for frontend compatibility
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    subCategory = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'price', 'originalPrice', 'image',
            'badge', 'category', 'subCategory', 'slug',
        ]

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))

    def get_subCategory(self, obj):
        return obj.sub_category.slug if obj.sub_category else None


class ProductDetailSerializer(serializers.ModelSerializer):
    """For detail view: adds images, description, sub_category."""
    id = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    originalPrice = serializers.DecimalField(
        source='original_price', max_digits=10, decimal_places=2,
        read_only=True, allow_null=True
    )
    # Return category and subcategory slugs for frontend compatibility
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    subCategory = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'slug', 'price', 'originalPrice', 'image', 'images',
            'badge', 'category', 'subCategory', 'description',
            'is_featured', 'created_at',
        ]

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))

    def get_images(self, obj):
        qs = obj.images.all()
        req = self.context.get('request')
        return [_image_url(i.image, req) for i in qs] if qs.exists() else []

    def get_subCategory(self, obj):
        return obj.sub_category.slug if obj.sub_category else None


class SubcategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategories (children of main categories)."""
    href = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'href', 'order']

    def get_href(self, obj):
        """Generate URL for subcategory: /parent-slug?type=subcategory-slug"""
        if obj.parent:
            return f"/{obj.parent.slug}?type={obj.slug}"
        return f"/{obj.slug}"

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for main categories with nested subcategories."""
    href = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'href', 'order', 'subcategories']

    def get_href(self, obj):
        return f"/{obj.slug}" if obj.slug else "/"

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))

    def get_subcategories(self, obj):
        """Return all active subcategories for this main category."""
        subcats = obj.get_subcategories()
        return SubcategorySerializer(subcats, many=True, context=self.context).data


class CategoryFlatSerializer(serializers.ModelSerializer):
    """Flat serializer for categories without nested subcategories."""
    href = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    parentSlug = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'href', 'order', 'parentSlug']

    def get_href(self, obj):
        if obj.parent:
            return f"/{obj.parent.slug}?type={obj.slug}"
        return f"/{obj.slug}"

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))

    def get_parentSlug(self, obj):
        return obj.parent.slug if obj.parent else None


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model used in homepage brand showcase."""
    image = serializers.SerializerMethodField()
    redirectUrl = serializers.URLField(source='redirect_url', read_only=True)
    brandType = serializers.CharField(source='brand_type', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'image', 'redirectUrl', 'brandType', 'order']

    def get_image(self, obj):
        return _image_url(obj.image, self.context.get('request'))
