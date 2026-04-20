from django.db import models
from util.mixin.base_mixin import BaseMixin


class Role(BaseMixin):
    name = models.CharField(max_length=100)
    code_name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField('Permission', related_name='+')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
