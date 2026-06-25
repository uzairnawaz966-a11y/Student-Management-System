from rest_framework import serializers
from django.core.validators import validate_email
from organization.models import Organization, OrganizationJoinLink, Membership
from django.core.exceptions import ValidationError as DjangoValidationError


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
            "max_users",
            "allowed_emails"
        ]
        extra_kwargs = {
            "max_users": {"required": True},
            "allowed_emails": {"required": True}
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

    def validate_allowed_emails(self, value):
        request = self.context["request"]
        organization = request.membership.organization

        if not value:
            raise serializers.ValidationError("No emails provided")

        normalized = []

        for email in value:

            if Membership.objects.filter(organization=organization, user__email=email).exists():
                raise serializers.ValidationError(f"{email} already registered for this organization")

            try:
                validate_email(email)
            except DjangoValidationError:
                raise serializers.ValidationError(f"{email} is not a valid email address")

            normalized.append(email)

        return normalized

class JoinLinkDetailSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    creator = serializers.CharField(source="created_by.user", read_only=True)
    
    class Meta:
        model = OrganizationJoinLink
        fields = [
            "organization_id",
            "organization_name",
            "creator",
            "status"
        ]


class JoinLinkValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        invite_link = self.context.get("invite_link")

        if not invite_link.is_valid:
            raise serializers.ValidationError("Link disabled")

        if (
            invite_link.max_users is not None
            and invite_link.used_count >= invite_link.max_users
        ):
            raise serializers.ValidationError("Join link usage limit exceeded")
    
        email = attrs.get("email")

        allowed_emails = invite_link.allowed_emails

        if email not in allowed_emails:
            raise serializers.ValidationError(
                "Email is not authorized for this invite link"
            )

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