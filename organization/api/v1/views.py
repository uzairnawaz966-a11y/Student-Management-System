from rest_framework import viewsets, status
from rest_framework.response import Response
from organization.api.v1.serializers import OrganizationJoinLinkSerializer
from organization.models import OrganizationJoinLink
from organization.services.join_link_service import OrganizationJoinLinkService
from rest_framework.permissions import IsAuthenticated
from organization.permissions import OrganizationJoinLinkGenerationPermission
from rest_framework.decorators import action


class OrganizationJoinLinkViewset(viewsets.ModelViewSet):
    queryset = OrganizationJoinLink.objects.all()
    serializer_class = OrganizationJoinLinkSerializer
    permission_classes = [IsAuthenticated, OrganizationJoinLinkGenerationPermission]
    http_method_names = ["post"]

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