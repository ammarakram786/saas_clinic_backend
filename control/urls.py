from django.urls import path, include
from rest_framework.routers import DefaultRouter

from control.views import (
    TenantViewSet,
    FeatureViewSet,
    PackageViewSet,
    SubscriptionViewSet,
    PlatformLoginView,
    PlatformLogoutView,
    PlatformRefreshView,
    CurrentPlatformUserView,
    PlatformUserViewSet,
    PlatformRoleViewSet,
    PlatformPermissionViewSet,
    PlatformAuditLogViewSet,
    PlatformStatsView,
)


router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='platform-tenant')
router.register(r'features', FeatureViewSet, basename='platform-feature')
router.register(r'packages', PackageViewSet, basename='platform-package')
router.register(r'subscriptions', SubscriptionViewSet, basename='platform-subscription')
router.register(r'platform-users', PlatformUserViewSet, basename='platform-user')
router.register(r'platform-roles', PlatformRoleViewSet, basename='platform-role')
router.register(r'platform-permissions', PlatformPermissionViewSet, basename='platform-permission')
router.register(r'audit-logs', PlatformAuditLogViewSet, basename='platform-audit-log')


urlpatterns = [
    path('auth/login/', PlatformLoginView.as_view(), name='platform-login'),
    path('auth/logout/', PlatformLogoutView.as_view(), name='platform-logout'),
    path('auth/refresh/', PlatformRefreshView.as_view(), name='platform-refresh'),
    path('auth/me/', CurrentPlatformUserView.as_view(), name='platform-me'),

    path('stats/', PlatformStatsView.as_view(), name='platform-stats'),

    path('', include(router.urls)),
]
