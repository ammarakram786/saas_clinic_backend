import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class PlatformPermission(models.Model):
    """
    Platform-plane permission. Code names are prefixed ``platform.*``.
    """

    code_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, default='')
    is_builtin = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'platform_permission'
        ordering = ('module', 'code_name')
        verbose_name = 'Platform Permission'
        verbose_name_plural = 'Platform Permissions'

    def __str__(self):
        return self.code_name


class PlatformRole(models.Model):
    name = models.CharField(max_length=100)
    code_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True, default='')
    permissions = models.ManyToManyField(PlatformPermission, related_name='roles')

    class Meta:
        db_table = 'platform_role'
        verbose_name = 'Platform Role'
        verbose_name_plural = 'Platform Roles'

    def __str__(self):
        return self.name


class PlatformUserManager(BaseUserManager):
    def _validate_email(self, email):
        if not email:
            raise ValueError('Email is required.')
        return self.normalize_email(email)

    def create_user(self, email, password=None, **extra):
        email = self._validate_email(email)
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_active', True)
        return self.create_user(email=email, password=password, **extra)


class PlatformUser(AbstractBaseUser):
    """
    Control-plane identity. Separate table and separate auth from
    ``account.User`` (which belongs to the tenant plane).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    mfa_enabled = models.BooleanField(default=False)

    role = models.ForeignKey(
        PlatformRole, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='users',
    )

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlatformUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = 'platform_user'
        verbose_name = 'Platform User'
        verbose_name_plural = 'Platform Users'

    def get_full_name(self):
        return self.full_name or self.email

    def get_short_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.email

    def __str__(self):
        return self.email
