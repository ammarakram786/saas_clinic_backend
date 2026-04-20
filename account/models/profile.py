from django.db import models
import uuid
from util.mixin.base_mixin import BaseMixin


def get_profile_image_path(self, filename):
    return f'profile_images/users/{self.pk}/{str(uuid.uuid4())}.png'


def get_default_profile_image_path():
    return f'profile_images/default_profile_image.png'


class Profile(BaseMixin):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to=get_profile_image_path, default=get_default_profile_image_path, null=True, blank=True)
    user = models.OneToOneField('account.User', on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"""{self.first_name} - {self.last_name}"""

    class Meta:
        db_table = 'profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

