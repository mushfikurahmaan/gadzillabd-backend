from rest_framework import viewsets, mixins

from config.permissions import IsStaffUser
from .models import ContactSubmission
from .admin_serializers import AdminContactSubmissionSerializer


class AdminContactSubmissionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsStaffUser]
    serializer_class = AdminContactSubmissionSerializer
    queryset = ContactSubmission.objects.all()
