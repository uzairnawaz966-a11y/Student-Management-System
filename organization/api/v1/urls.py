from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization.api.v1.views import OrganizationJoinLinkViewset


router = DefaultRouter()

router.register(r'join-link', OrganizationJoinLinkViewset, basename="join-link")


urlpatterns = [
    path('', include(router.urls)),
]