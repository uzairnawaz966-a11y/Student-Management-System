from organization.models import OrganizationJoinLink
from rest_framework.exceptions import PermissionDenied
from django.conf import settings


class OrganizationJoinLinkService:

    @staticmethod
    def generate_join_link(membership, max_users=None):
        if membership.is_owner:

            link = OrganizationJoinLink.objects.create(
                organization=membership.organization,
                created_by=membership,
                role=membership.role,
                max_users=max_users
            )

            organization_join_url = f"{settings.ORGANIZATION_BASE_URL}/student-management-system/join/{link.token}/"

            return organization_join_url
        else:
            raise PermissionDenied("Only owners can create join links")