from organization.models import OrganizationJoinLink
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from django.conf import settings


class OrganizationJoinLinkService:

    @staticmethod
    def create_join_link(membership, role, max_users=None):

        link = OrganizationJoinLink.objects.create(
            organization=membership.organization,
            created_by=membership,
            role=role,
            max_users=max_users,
            is_valid=True
        )

        organization_join_url = f"{settings.ORGANIZATION_BASE_URL}/student-management-system/join/{link.token}/"

        return organization_join_url


class OrganizationJoinLinkService:

    @staticmethod
    def disable_link(invite_link, membership):

        if not membership.is_owner or not membership.is_admin:
            raise PermissionDenied("Not allowed to disable this link")

        invite_link.status = OrganizationJoinLink.Status.DISABLED
        invite_link.is_expired = True
        invite_link.expired_at = timezone.now()

        invite_link.save(
            update_fields=[
                "status",
                "is_expired",
                "expired_at"
            ]
        )

        return invite_link


    # @staticmethod
    # def accept_join(token, user):
    #     try:
    #         link = OrganizationJoinLink.objects.get(token=token)
    #     except OrganizationJoinLink.DoesNotExist:
    #         raise ValueError("Invalid join link")

    #     if link.status == OrganizationJoinLink.Status.ACTIVE:
    #         if link.used_count > link.max_users:
    #             raise PermissionDenied("Max limit reached")
    #     else:
    #         raise PermissionDenied("Link disabled")