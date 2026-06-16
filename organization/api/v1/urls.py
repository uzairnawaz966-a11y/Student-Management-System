from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization.api.v1.views import (
    OrganizationCreateAPIView,
    OrganizationJoinLinkViewset,
    RetrieveInviteLinkAPIView,
    RegisterFromInviteAPIView,
)


router = DefaultRouter()

router.register(r'join-link', OrganizationJoinLinkViewset, basename="join-link")


urlpatterns = [
    path('', include(router.urls)),
    path("create/", OrganizationCreateAPIView.as_view(), name="organization-create"),
    path("invite/<uuid:token>/validate/", RetrieveInviteLinkAPIView.as_view(), name="validate-invite"),
    path("student-management-system/join/<uuid:token>/", RegisterFromInviteAPIView.as_view(), name="register-invite")
]