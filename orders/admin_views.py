from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsStaffUser
from .models import Order
from .admin_serializers import (
    AdminOrderListSerializer,
    AdminOrderSerializer,
    AdminOrderStatusSerializer,
)


class AdminOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsStaffUser]
    queryset = Order.objects.prefetch_related('items__product').all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            return AdminOrderListSerializer
        return AdminOrderSerializer

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = AdminOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status'])
        return Response(AdminOrderSerializer(order).data)

    @action(detail=True, methods=['patch'], url_path='tracking')
    def update_tracking(self, request, pk=None):
        order = self.get_object()
        tracking = request.data.get('tracking_number', '')
        order.tracking_number = tracking
        order.save(update_fields=['tracking_number'])
        return Response(AdminOrderSerializer(order).data)
