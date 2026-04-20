from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid


def get_profile_image_path(self, filename):
    return f'profile_images/users/{self.pk}/{str(uuid.uuid4())}.png'

def get_default_profile_image_path():
    return f'profile_images/default_profile_image.png'

class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('User must have a username.')
        user = self.model(username=username)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):    
    username = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.CharField(max_length=255, unique=True, null=True, blank=True)
    role = models.ForeignKey("account.Role", on_delete=models.SET_NULL, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'

