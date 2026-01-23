from rest_framework import serializers

from products.serializers import ProductListSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'size', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'email', 'status', 'total', 'shipping_name', 'shipping_address',
            'phone', 'delivery_area', 'tracking_number', 'created_at', 'updated_at', 'items',
        ]


class OrderCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    shipping_name = serializers.CharField(max_length=255)
    shipping_address = serializers.CharField()

    def validate_shipping_name(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Required.')
        return value.strip()

    def validate_shipping_address(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Required.')
        return value.strip()


class DirectOrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders directly with products (not from cart)."""
    shipping_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    shipping_address = serializers.CharField()
    delivery_area = serializers.CharField(max_length=50)
    products = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )

    def validate_shipping_name(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Required.')
        return value.strip()

    def validate_phone(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Required.')
        return value.strip()

    def validate_shipping_address(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Required.')
        return value.strip()

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('At least one product is required.')
        for product in value:
            if 'id' not in product or 'quantity' not in product:
                raise serializers.ValidationError('Each product must have id and quantity.')
        return value
