from rest_framework import viewsets

from config.permissions import IsStaffUser
from .models import Notification
from .admin_serializers import AdminNotificationSerializer


class AdminNotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    serializer_class = AdminNotificationSerializer
    queryset = Notification.objects.all()
