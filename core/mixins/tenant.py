def get_membership(user, org_id):
    """
    Accepts a user and organization_id
    returns the membership of the user in the given organization id
    Organization id will come in the headers from frontend
    """

    if not user or not user.is_authenticated:
        return None

    try:
        org_id = int(org_id)
    except (TypeError, ValueError):
        return None

    return user.memberships.filter(
        organization_id=org_id,
        is_active=True
    ).first()


class OrganizationScopeMixin:
    """
    Mixin for views which fetches the organizatino and membership of the user within the organization
    Stops repeating the same logic again and again
    """

    def get_membership(self):
        if hasattr(self, "_membership"):
            return self._membership

        org_id = self.request.auth.get(
            "organization_id"
        )
        self._membership = get_membership(self.request.user, org_id)
        return self._membership






# ----- Token Payload -----

# {
#   "token_type": "access",
#   "exp": 1776866932,
#   "iat": 1776863332,
#   "jti": "9abcfb3432b6441898d74f621a335894",
#   "user_id": "38",
#   "organization_id": 3,
#   "role": "INSTRUCTOR"
# }