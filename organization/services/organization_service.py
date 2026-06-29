from organization.models import Organization, Membership
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError


class OrganizationService:

    @staticmethod
    def create_organization(user, validated_data):
        try:
            with transaction.atomic():

                if not user.is_active:
                    raise ValidationError("Your account is not active. Please verify your email first")
                
                if Organization.objects.filter(owner=user).exists():
                    raise ValidationError("You already own an organization")

                organization = Organization.objects.create(
                    owner=user,
                    **validated_data
                )

                membership = Membership.objects.create(
                    user=user,
                    organization=organization,
                    role=Membership.Role.OWNER,
                    is_active=True
                )
            return organization, membership

        except IntegrityError:
            raise ValidationError("Membership already exist")