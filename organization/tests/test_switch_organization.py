from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from organization.models import Organization, Membership

User = get_user_model()


class SwitchOrganizationAPIViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="uzair",
            password="testuser@123"
        )

        self.client.force_authenticate(self.user)

        self.url = reverse("switch-organization")

        self.organization_1 = Organization.objects.create(
            owner=self.user,
            name="Organization One",
            description="Description"
        )

        self.organization_2 = Organization.objects.create(
            owner=self.user,
            name="Organization Two",
            description="Description"
        )

        self.active_membership = Membership.objects.create(
            user=self.user,
            organization=self.organization_2,
            role=Membership.Role.STUDENT,
            is_active=True
        )


    def test_user_can_switch_organization_successfully(self):
        payload = {
            "organization_id": self.organization_2.id
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Organization switched successfully")
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["membership"]["organization_id"], self.organization_2.id)
        self.assertEqual(response.data["membership"]["role"], Membership.Role.STUDENT)


    def test_unauthenticated_user_cannot_switch_organization(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(self.url, {"organization_id": self.organization_2.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_switch_organization_requires_organization_id(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization_id", response.data)


    def test_switch_organization_with_invalid_organization_id_type(self):
        response = self.client.post(self.url, {"organization_id": "invalid"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization_id", response.data)


    def test_user_cannot_switch_to_organization_without_membership(self):
        another_organization = Organization.objects.create(
            owner=self.user,
            name="Organization Three",
            description="Description"
        )

        Membership.objects.filter(
            user=self.user,
            organization=another_organization
        ).delete()

        response = self.client.post(self.url, {"organization_id": another_organization.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization_id", response.data)


    def test_user_cannot_switch_to_organization_with_inactive_membership(self):
        inactive_organization = Organization.objects.create(
            owner=self.user,
            name="Inactive Organization",
            description="Description"
        )

        Membership.objects.create(
            user=self.user,
            organization=inactive_organization,
            role=Membership.Role.STUDENT,
            is_active=False
        )

        response = self.client.post(self.url, {"organization_id": inactive_organization.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization_id", response.data)


    def test_refresh_token_contains_custom_claims(self):
        response = self.client.post(self.url, {"organization_id": self.organization_2.id}, format="json")

        refresh_token = response.data["tokens"]["refresh"]

        token = RefreshToken(refresh_token)

        self.assertEqual(token["organization_id"], self.organization_2.id)
        self.assertEqual(token["role"], Membership.Role.STUDENT)


    def test_switch_to_non_existent_organization_returns_400(self):
        payload = {
            "organization_id": 99999999
        }

        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_switch_to_null_organization_id_returns_400(self):
        payload = {
            "organization_id": None
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_switch_with_empty_payload_returns_400(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_user_with_multiple_memberships_switches_correctly(self):
        org3 = Organization.objects.create(
            owner=self.user,
            name="Org 3",
            description="Desc"
        )

        Membership.objects.create(
            user=self.user,
            organization=org3,
            role=Membership.Role.ADMIN,
            is_active=True
        )

        payload = {"organization_id": org3.id}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["membership"]["organization_id"], org3.id)

    def test_token_changes_when_switching_organization(self):
        payload = {
            "organization_id": self.organization_2.id
        }

        response1 = self.client.post(self.url, payload, format="json")
        token1 = response1.data["tokens"]["access"]

        response2 = self.client.post(self.url, payload, format="json")
        token2 = response2.data["tokens"]["access"]

        self.assertNotEqual(token1, token2)


    def test_switch_returns_correct_membership_role(self):
        self.active_membership.role = Membership.Role.INSTRUCTOR
        self.active_membership.save()

        payload = {
            "organization_id": self.organization_2.id
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.data["membership"]["role"], Membership.Role.INSTRUCTOR)


    def test_response_structure_is_consistent(self):
        payload = {
            "organization_id": self.organization_2.id
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertIn("message", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("membership", response.data)
        self.assertIn("organization_id", response.data["membership"])
        self.assertIn("role", response.data["membership"])


    def test_user_cannot_switch_using_other_users_membership(self):
        second_user = User.objects.create_user(
            username="otheruser",
            email="other@test.com",
            password="testpass123"
        )

        second_org = Organization.objects.create(
            owner=second_user,
            name="Other Org",
            description="Desc"
        )

        Membership.objects.create(
            user=second_user,
            organization=second_org,
            role=Membership.Role.ADMIN,
            is_active=True
        )

        response = self.client.post(
            self.url,
            {"organization_id": second_org.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_switching_to_same_organization_twice_is_safe(self):
        payload = {
            "organization_id": self.organization_2.id
        }

        response_1 = self.client.post(self.url, payload, format="json")
        response_2 = self.client.post(self.url, payload, format="json")

        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)


    def test_switch_fails_if_membership_is_inactive_state(self):
        Membership.objects.filter(id=self.active_membership.id).update(is_active=False)

        response = self.client.post(self.url, {"organization_id": self.organization_2.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_response_schema_is_consistent(self):
        response = self.client.post(self.url, {"organization_id": self.organization_2.id}, format="json")

        self.assertSetEqual(set(response.data.keys()), {"message", "tokens", "membership"})
        self.assertSetEqual(set(response.data["tokens"].keys()), {"access", "refresh"})
        self.assertSetEqual(set(response.data["membership"].keys()), {"organization_id", "role"})


    def test_missing_description_returns_400(self):
        response = self.client.post(self.url, {"name": "Org Only Name"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_blank_name_returns_400(self):
        response = self.client.post(self.url, {"name": "    ","description": "sadjfkhalskdjfhlkjashdf"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_very_long_name_returns_400_or_accepted(self):
        payload = {
            "name": "x" * 500,
            "description": "jasdhflashfjhsdlkfhaslkjdhlkajsf"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)


    def test_create_response_schema_is_valid(self):
        response = self.client.post(
            self.url,
            {"organization_id": self.organization_2.id},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("message", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("membership", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("organization_id", response.data["membership"])
        self.assertIn("role", response.data["membership"])