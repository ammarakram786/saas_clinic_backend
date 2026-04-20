from django.urls import path, include
from rest_framework.routers import DefaultRouter
from account.views import (
    LoginView,
    LogoutView,
    RefreshView,
    CurrentUserView,
    UserViewSet,
    UserListViewSet,
    RoleViewSet,
    PermissionListView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'users-list', UserListViewSet, basename='user-list')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'profiles', RoleViewSet, basename='profile')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshView.as_view(), name='refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),

    path('', include(router.urls)),
]
