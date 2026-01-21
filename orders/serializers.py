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
            'tracking_number', 'created_at', 'updated_at', 'items',
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
