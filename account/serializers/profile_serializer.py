from rest_framework import serializers
from account.models import Profile
from util.mixin.audit_mixin import AuditMixin

class ProfileSerializer(AuditMixin, serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id', 'first_name', 'last_name', 'mobile_number', 'dob', 'user'
        )


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep





