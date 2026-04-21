from django.core.validators import RegexValidator
from django.db import models

from util.mixin.base_mixin import BaseMixin


feature_code_validator = RegexValidator(
    regex=r'^[a-z][a-z0-9_\-]{1,63}$',
    message='Feature code must be lowercase, alphanumeric, underscore or hyphen.',
)


class Feature(BaseMixin):
    code = models.CharField(
        max_length=64, unique=True, validators=[feature_code_validator], db_index=True,
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=64, blank=True, default='')

    class Meta:
        db_table = 'platform_feature'
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'
        ordering = ('category', 'code')

    def __str__(self):
        return self.code
