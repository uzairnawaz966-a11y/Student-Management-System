from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from organization.models import Membership
from django.http import JsonResponse


class OrganizationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        request.membership = None
        request.organization_id = None
        request.role = None

        jwt_auth = JWTAuthentication()

        try:
            auth_result = jwt_auth.authenticate(request)
        except (InvalidToken, TokenError):
            return JsonResponse(
                {
                    "detail": "Invalid or expired token"
                },
                status=401
            )

        if not auth_result:
            return JsonResponse(
                {
                    "detail": "Invalid Token"
                },
                status=403
            )

        user, token = auth_result

        organization_id = token.get("organization_id")
        role = token.get("role")

        if not organization_id:
            return JsonResponse(
                {
                    "detail": "Missing Organization"
                },
                status=403
            )

        try:
            membership = Membership.objects.get(
                user=user,
                organization_id=organization_id,
                role=role,
                is_active=True
            )

        except Membership.DoesNotExist:
            return JsonResponse(
                {
                    "detail": "Invalid Membership"
                },
                status=403
            )

        request.membership = membership
        request.organization_id = organization_id
        request.role = role
        
        response = self.get_response(request)
        return response


















# class CurrentOrganizationMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         user = request.user

#         request.membership = None
#         request.organization = None

#         if user.is_authenticated:
#             org_id = request.headers.get(
#                 "X-Organization-ID"
#             )
#             if org_id:

#                 try:
#                     org_id = int(org_id)
#                 except (TypeError, ValueError):
#                     return self.get_response(request)

#                 membership = user.memberships.filter(
#                     organization_id=org_id,
#                     is_active=True
#                 ).first()
#                 if membership:
#                     request.membership = membership
#                     request.organization = membership.organization
#                 else:
#                     ...


#         print("User: ", request.user)
#         print("HEADER: ", request.headers)
#         print("MEMBERSHIP: ", request.membership)

#         return self.get_response(request)















# from django.core.exceptions import PermissionDenied
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed


# class JWTCrossAuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # 1. Initialize the JWT Auth class
#         jwt_authenticator = JWTAuthentication()

#         try:
#             # 2. Try to authenticate the request
#             # This looks for the 'Authorization: Bearer <token>' header
#             auth_res = jwt_authenticator.authenticate(request)

#             if auth_res is not None:
#                 # auth_res is a tuple: (user, validated_token)
#                 user, token = auth_res
#                 request.user = user  # Manually attach user to request
#             else:
#                 request.user = None  # Or handle as AnonymousUser
#         except AuthenticationFailed as e:
#             # Token is invalid, expired, or not provided
#             request.user = None

#         # 3. Now you can perform your Cross-Authorization
#         if request.user and request.user.is_authenticated:
#             user_attr = getattr(request.user, 'custom_attribute', None)
#             # Perform your cross-auth logic here...
#             # Example: if user_attr != "Allowed": raise PermissionDenied()

#         return self.get_response(request)