
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from util.mixin.view_mixin import AuditViewSetMixin
from util.permissions import DynamicRolePermission


class BaseAuditViewSet(AuditViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DynamicRolePermission)
    filter_backends = (filters.DjangoFilterBackend,)

    class Meta:
        abstract = True