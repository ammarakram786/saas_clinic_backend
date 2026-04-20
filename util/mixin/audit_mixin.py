class AuditBase:
    @staticmethod
    def _get_user_info(user):
        if not user:
            return None
        get_full_name = getattr(user, 'get_full_name', None)
        full_name = get_full_name() if callable(get_full_name) else None
        return {
            'id': user.id,
            'username': getattr(user, 'username', None) or getattr(user, 'email', None),
            'full_name': full_name or getattr(user, 'username', None) or getattr(user, 'email', ''),
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
