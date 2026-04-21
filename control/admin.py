from django.contrib import admin

from control.models import (
    Feature,
    Package,
    PackageFeature,
    PlatformAuditLog,
    PlatformPermission,
    PlatformRole,
    PlatformUser,
    Tenant,
    TenantFeatureOverride,
    TenantSubscription,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'status', 'onboarded_at')
    list_filter = ('status',)
    search_fields = ('name', 'slug', 'contact_email')
    readonly_fields = ('limits_snapshot',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')


class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 0


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'currency', 'price_monthly', 'is_public', 'is_active')
    list_filter = ('is_public', 'is_active', 'currency')
    search_fields = ('code', 'name')
    inlines = (PackageFeatureInline,)


@admin.register(TenantSubscription)
class TenantSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'package', 'status', 'billing_cycle', 'starts_at', 'ends_at')
    list_filter = ('status', 'billing_cycle')
    search_fields = ('tenant__slug', 'package__code')


@admin.register(TenantFeatureOverride)
class TenantFeatureOverrideAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'feature', 'is_enabled', 'limit_value', 'expires_at')
    list_filter = ('is_enabled',)
    search_fields = ('tenant__slug', 'feature__code')


@admin.register(PlatformUser)
class PlatformUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'last_login_at')
    list_filter = ('is_active', 'role')
    search_fields = ('email', 'full_name')


@admin.register(PlatformRole)
class PlatformRoleAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'name')
    search_fields = ('code_name', 'name')
    filter_horizontal = ('permissions',)


@admin.register(PlatformPermission)
class PlatformPermissionAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'name', 'module')
    list_filter = ('module',)
    search_fields = ('code_name', 'name')


@admin.register(PlatformAuditLog)
class PlatformAuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'resource_type', 'resource_id', 'actor', 'tenant')
    list_filter = ('action', 'resource_type')
    search_fields = ('resource_type', 'resource_id', 'request_id')
    readonly_fields = tuple(f.name for f in PlatformAuditLog._meta.fields)
