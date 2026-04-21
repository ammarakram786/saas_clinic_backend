from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from control.context import get_current_tenant
from account.permissions import IsTenantStaff
from account.serializers import UserSerializer
from account.util import combine_role_permissions
from account.models import TenantMembership


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated, IsTenantStaff)

    def get(self, request):
        data = UserSerializer(request.user, context={'request': request}).data
        tenant = get_current_tenant()
        membership = None
        if tenant is not None:
            membership = (
                TenantMembership.objects.select_related('role', 'tenant')
                .filter(user=request.user, tenant=tenant, is_active=True)
                .first()
            )
        if membership is not None:
            data['tenant'] = {
                'id': membership.tenant_id,
                'name': membership.tenant.name,
                'slug': membership.tenant.slug,
            }
            data['membership_id'] = membership.pk
            data['permissions'] = combine_role_permissions(membership.role)
        else:
            data['permissions'] = []
        return Response({"user": data}, status=status.HTTP_200_OK)
