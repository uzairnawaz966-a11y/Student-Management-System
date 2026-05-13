from rest_framework import serializers
from organization.models import OrganizationJoinLink, Membership


class OrganizationJoinLinkSerializer(serializers.ModelSerializer):    
    class Meta:
        model = OrganizationJoinLink
        fields = [
            "role",
            "max_users"
        ]
        extra_kwargs = {
            "max_users": {"required": True}
        }

    def validate(self, attrs):
        request = self.context.get("request")
        membership = request.membership
        role = attrs.get("role")
        allowed_roles = [
            Membership.Role.ADMIN,
            Membership.Role.INSTRUCTOR,
            Membership.Role.STUDENT
        ]

        if membership.is_admin:
            if role not in allowed_roles:
                raise serializers.ValidationError("Not allowed to create link for this role")

        return attrs