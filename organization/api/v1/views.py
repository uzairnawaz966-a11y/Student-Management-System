from rest_framework import viewsets, status
from rest_framework.response import Response
from organization.models import OrganizationJoinLink
from organization.services.join_link_service import OrganizationJoinLinkService
from rest_framework.permissions import IsAuthenticated
from organization.permissions import OrganizationJoinLinkGenerationPermission
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from organization.api.v1.serializers import (
    OrganizationJoinLinkSerializer,
    JoinLinkValidationSerializer,
    JoinLinkDetailSerializer
)


class OrganizationJoinLinkViewset(viewsets.ModelViewSet):
    queryset = OrganizationJoinLink.objects.all()
    serializer_class = OrganizationJoinLinkSerializer
    permission_classes = [IsAuthenticated, OrganizationJoinLinkGenerationPermission]
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

    @action(detail=False, methods=["get"], url_path="(?P<token>[^/.]+)")
    def retrieve_invite_link(self, request, token=None):
        invite_link = get_object_or_404(
            OrganizationJoinLink,
            token=token
        )

        validation_serializer = JoinLinkValidationSerializer(
            data={},
            context={
                "invite_link": invite_link
            }
        )
        validation_serializer.is_valid(raise_exception=True)

        detail_serializer = JoinLinkDetailSerializer(invite_link)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)