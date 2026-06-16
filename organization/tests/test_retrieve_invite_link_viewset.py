from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from organization.models import (
    Organization,
    Membership,
    OrganizationJoinLink
)

User = get_user_model()


class RetrieveInviteLinkAPIViewTests(APITestCase):

    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner",
            password="testpass123"
        )

        self.organization = Organization.objects.create(
            name="ENIGMATIX",
            owner=self.owner_user
        )

        self.owner_membership = Membership.objects.create(
            user=self.owner_user,
            organization=self.organization,
            role=Membership.Role.OWNER,
            is_active=True
        )

        self.invite_link = OrganizationJoinLink.objects.create(
            organization=self.organization,
            created_by=self.owner_membership,
            role=Membership.Role.STUDENT,
            max_users=10,
            used_count=0
        )

    def test_valid_invite_link_returns_link_details(self):

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_non_existent_invite_link_returns_404(self):

        url = reverse(
            "validate-invite",
            args=["11111111-1111-1111-1111-111111111111"]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_disabled_invite_link_returns_400(self):

        self.invite_link.status = OrganizationJoinLink.Status.DISABLED
        self.invite_link.save()

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_invite_link_with_usage_limit_reached_returns_400(self):

        self.invite_link.used_count = self.invite_link.max_users
        self.invite_link.save()

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_invite_link_returns_correct_organization(self):

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["organization"],
            self.organization.id
        )

    def test_invite_link_returns_correct_creator_membership(self):

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["created_by"],
            self.owner_membership.id
        )

    def test_invite_link_returns_correct_status(self):

        url = reverse(
            "validate-invite",
            args=[self.invite_link.token]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["status"],
            self.invite_link.status
        )