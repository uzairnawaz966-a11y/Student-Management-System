from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from organization.models import Membership


class OrganizationJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            return None

        user, token = result

        organization_id = token.get("organization_id")
        role = token.get("role")

        if not organization_id:
            raise AuthenticationFailed("Missing organization_id in the token")

        try:
            membership = Membership.objects.get(
                user=user,
                organization_id=organization_id,
                role=role,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise AuthenticationFailed("Membership does not exist")

        request.membership = membership
        request.organization_id = organization_id
        request.role = role

        return (user, token)