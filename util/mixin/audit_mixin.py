class AuditBase:
    @staticmethod
    def _get_user_info(user):
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username
        }

    @classmethod
    def attach_audit_fields(cls, instance, data):
        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        data['created_by'] = cls._get_user_info(instance.created_by)
        data['updated_by'] = cls._get_user_info(instance.updated_by)
        return data


class AuditMixin:

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return AuditBase.attach_audit_fields(instance, data)