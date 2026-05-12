from rest_framework.permissions import BasePermission
from organization.models import Membership


class OrganizationJoinLinkGenerationPermission(BasePermission):

    def has_permission(self, request, view):
        membership = request.membership

        return membership.role in [
            Membership.Role.OWNER,
            Membership.Role.ADMIN
        ]