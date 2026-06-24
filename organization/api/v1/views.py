from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from organization.models import OrganizationJoinLink
from organization.services.join_link_service import OrganizationJoinLinkService
from organization.services.organization_service import OrganizationService
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from organization.permissions import JoinLinkViewSetPermission
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from user_auth.api.v1.serializers import RegisterSerializer
from user_auth.services.auth_service import AuthService
from rest_framework_simplejwt.tokens import RefreshToken
from organization.models import Membership
from organization.api.v1.serializers import (
    OrganizationCreateSerializer,
    OrganizationJoinLinkSerializer,
    SwitchOrganizationSerializer,
    JoinLinkValidationSerializer,
    JoinLinkDetailSerializer
)

User = get_user_model()

"""
[email] [hit enter] -> (check email linked with any org or not) -> If linked -> show linked organization
                                                                -> if not linked -> 1) ask user input for new organization name  -> call org create api if created -> then ask for user metadata (password, name etc)
"""


class OrganizationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization, membership = OrganizationService.create_organization(
            user=request.user,
            validated_data=serializer.validated_data
        )

        return Response(
            {
                "message": "Organization created successfully",
                "organization": {
                    "id": organization.id,
                    "owner": organization.owner.id,
                    "name": organization.name
                },
                "membership": {
                    "role": membership.role
                }
            },
            status=status.HTTP_201_CREATED
        )


class SwitchOrganizationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SwitchOrganizationSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(raise_exception=True)

        organization_id = serializer.validated_data["organization_id"]

        membership = Membership.objects.get(
            user=request.user,
            organization_id=organization_id,
            is_active=True
        )

        refresh = RefreshToken.for_user(request.user)

        refresh["organization_id"] = membership.organization_id
        refresh["role"] = membership.role

        return Response({
            "message": "Organization switched successfully",
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            },
            "membership": {
                "organization_id": membership.organization_id,
                "role": membership.role
            }
        })


class OrganizationJoinLinkViewset(viewsets.ModelViewSet):
    queryset = OrganizationJoinLink.objects.all()
    serializer_class = OrganizationJoinLinkSerializer
    permission_classes = [IsAuthenticated, JoinLinkViewSetPermission]
    http_method_names = ["post", "get"]

    def get_queryset(self):
        return OrganizationJoinLink.objects.filter(
            organization=self.request.membership.organization
        )

    def create(self, request, *args, **kwargs):
        membership = request.membership
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request
            }
        )
        serializer.is_valid(raise_exception=True)

        link = OrganizationJoinLinkService.create_join_link(
            membership=membership,
            role=serializer.validated_data.get("role"),
            max_users=serializer.validated_data.get("max_users")
        )

        return Response(
            {
                "message": "Invite link created successfully",
                "invite_link": link,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def disable(self, request, pk=None):

        membership = request.membership

        invite_link = get_object_or_404(
            OrganizationJoinLink,
            pk=pk,
            organization=membership.organization
        )

        updated_link = OrganizationJoinLinkService.disable_link(
            invite_link=invite_link,
            membership=membership
        )

        return Response(
            {
                "message": "Invite link disabled successfully",
                "token": updated_link.token,
                "status": updated_link.status
            },
            status=status.HTTP_200_OK
        )


class RetrieveInviteLinkAPIView(APIView):
    def post(self, request, token):
        invite_link = get_object_or_404(
            OrganizationJoinLink,
            token=token
        )

        validation_serializer = JoinLinkValidationSerializer(
            data=request.data,
            context={
                "invite_link": invite_link
            }
        )
        validation_serializer.is_valid(raise_exception=True)

        email = validation_serializer.validated_data["email"]

        email_exists = User.objects.filter(email=email).exists()

        detail_serializer = JoinLinkDetailSerializer(invite_link)
        return Response(
            {
                "valid": True,
                "email": email,
                "email_exists": email_exists,
                "next_step": "login" if email_exists else "signup",
                "invite": detail_serializer.data
            },
            status=status.HTTP_200_OK
        )


class RegisterFromInviteAPIView(APIView):
    """
    Fetches Invite link
    Validate user input credentials
    Checks email exists in allowed_emails
    Adds organization_id and role in the request data
    Calls create_account method which will creates inactive user and membership and sends activation link on the user's email
    """

    def post(self, request, token):
        invite_link = get_object_or_404(
            OrganizationJoinLink,
            token=token
        )
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        email = data["email"]

        if email not in invite_link.allowed_emails:
            return Response(
                {
                    "message": "Email is not authorized for this invite link"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        data["organization_id"] = invite_link.organization_id
        data["role"] = invite_link.role

        service = AuthService()
        response = service.create_account(data)

        return Response(response, status=status.HTTP_201_CREATED)


# class AcceptInviteAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, token):
#         invite_link = get_object_or_404(
#             OrganizationJoinLink,
#             token=token
#         )

#         user_email = request.user.email

#         if user_email not in invite_link.allowed_emails:
#             return Response(
#                 {"detail": "Not allowed for this invite"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         membership_exists = Membership.objects.filter(
#             user=request.user,
#             organization=invite_link.organization
#         ).exists()

#         if membership_exists:
#             return Response(
#                 {"detail": "Already a member"},
#                 status=status.HTTP_200_OK
#             )

#         Membership.objects.create(
#             user=request.user,
#             organization=invite_link.organization,
#             role=invite_link.role,
#             is_active=True
#         )

#         invite_link.used_count += 1
#         invite_link.save(update_fields=["used_count"])

#         return Response({
#             "message": "Joined organization successfully"
#         })