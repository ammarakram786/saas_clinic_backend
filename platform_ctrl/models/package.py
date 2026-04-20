from django.core.validators import RegexValidator
from django.db import models

from util.mixin.base_mixin import BaseMixin


package_code_validator = RegexValidator(
    regex=r'^[a-z][a-z0-9_\-]{1,63}$',
    message='Package code must be lowercase, alphanumeric, underscore or hyphen.',
)


class Package(BaseMixin):
    code = models.CharField(
        max_length=64, unique=True, validators=[package_code_validator], db_index=True,
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default='')
    currency = models.CharField(max_length=3, default='USD')
    price_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'platform_package'
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'
        ordering = ('sort_order', 'code')

    def __str__(self):
        return self.code


class PackageFeature(models.Model):
    """
    Join table between Package and Feature with a per-feature limit.

    ``limit_value = NULL`` means unlimited for that feature in that package.
    """

    package = models.ForeignKey(
        'platform_ctrl.Package', on_delete=models.CASCADE, related_name='package_features',
    )
    feature = models.ForeignKey(
        'platform_ctrl.Feature', on_delete=models.PROTECT, related_name='package_features',
    )
    limit_value = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'platform_package_feature'
        constraints = [
            models.UniqueConstraint(
                fields=['package', 'feature'], name='uniq_package_feature',
            ),
        ]

    def __str__(self):
        return f'{self.package.code}:{self.feature.code}'
