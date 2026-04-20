from account.models import AuditLog
from util.pagination import DynamicPagination


class AuditViewSetMixin:
    pagination_class = DynamicPagination
    def _log_action(self, instance, action):
        AuditLog.objects.create(
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            user=self.request.user
        )

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        self._log_action(instance, 'CREATE')

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        self._log_action(instance, 'UPDATE')

    def perform_destroy(self, instance):
        self._log_action(instance, 'DELETE')
        instance.delete()