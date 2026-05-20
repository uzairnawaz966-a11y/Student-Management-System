from rest_framework.permissions import BasePermission


# class JoinLinkPermission(BasePermission):
#     def has_permission(self, request, view):

#         action = getattr(view, "action", None)
#         membership = getattr(request, "membership", None)

#         if action == "create":
#             return membership is not None and membership.is_owner or membership.is_admin

#         if action == "list":
#             return membership is not None and membership.is_owner or membership.is_admin

#         if action == "retrieve_invite_link":
#             return True

#         if action == "register_from_invite_link":
#             return True

#         return False



class JoinLinkViewSetPermission(BasePermission):
    def has_permission(self, request, view):

        membership = request.membership
        action = getattr(view, "action", None)

        if action in ["create", "list", "disable"]:
            return membership.is_owner or membership.is_admin

        return False


class InviteLinkPublicPermission(BasePermission):

    def has_permission(self, request, view):
        return request.method in ["GET", "POST"]