from rest_framework import serializers
from organization.models import Organization, OrganizationJoinLink, Membership


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name",
            "description"
        ]


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
        role = attrs.get("role")
        allowed_roles = [
            Membership.Role.ADMIN,
            Membership.Role.INSTRUCTOR,
            Membership.Role.STUDENT
        ]

        if role == Membership.Role.OWNER:
            raise serializers.ValidationError("Cannot create invite link for OWNER role")

        if role not in allowed_roles:
            raise serializers.ValidationError("Invalid role for join link")

        return attrs


class JoinLinkDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationJoinLink
        fields = [
            "organization",
            "created_by",
            "status"
        ]


class JoinLinkValidationSerializer(serializers.Serializer):

    def validate(self, attrs):
        invite_link = self.context.get("invite_link")

        if not invite_link.is_valid:
            raise serializers.ValidationError("Link disabled")

        if invite_link.used_count >= invite_link.max_users:
            raise serializers.ValidationError("Join link usage limit exceeded")

        return attrs


class SwitchOrganizationSerializer(serializers.Serializer):
    organization_id = serializers.IntegerField()

    def validate_organization_id(self, attrs):

        user = self.context["request"].user

        membership = Membership.objects.filter(
                user=user,
                organization_id=attrs,
                is_active=True
        ).exists()

        if not membership:
            raise serializers.ValidationError(
                "You don't have access to this organization"
            )

        return attrs