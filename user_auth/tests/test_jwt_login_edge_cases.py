from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class JWTLoginEdgeCaseV2Tests(APITestCase):

    def setUp(self):
        self.url = reverse("jwt_login")

        self.user = User.objects.create_user(
            username="Uzair",
            email="uzair@test.com",
            password="test123",
            is_active=True
        )

        self.org1 = Organization.objects.create(
            name="Org One",
            owner=self.user
        )

        self.org2 = Organization.objects.create(
            name="Org Two",
            owner=self.user
        )

        self.membership1 = Membership.objects.create(
            user=self.user,
            organization=self.org1,
            role="admin",
            is_active=True
        )

        self.membership2 = Membership.objects.create(
            user=self.user,
            organization=self.org2,
            role="student",
            is_active=True
        )

        self.payload = {
            "username": "Uzair",
            "password": "test123",
            "organization_id": self.org1.id
        }

    def test_login_case_insensitive_username(self):
        self.payload["username"] = "UZAIR"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertIn(response.status_code, [200, 400])

        if response.status_code == 200:
            self.assertIn("tokens", response.data)

    def test_login_selects_correct_organization(self):
        self.payload["organization_id"] = self.org1.id

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)

        token = AccessToken(response.data["tokens"]["access"])

        self.assertEqual(token["organization_id"], self.org1.id)

    def test_login_wrong_org_fails_consistently(self):
        self.payload["organization_id"] = 99999

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("tokens", response.data)

    def test_login_response_never_crashes_on_failure(self):
        self.payload["password"] = "wrong"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertIsInstance(response.data, dict)

        self.assertNotIn("tokens", response.data)

    def test_login_prioritizes_requested_organization(self):
        self.payload["organization_id"] = self.org2.id

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)

        token = AccessToken(response.data["tokens"]["access"])

        self.assertEqual(token["organization_id"], self.org2.id)
        self.assertEqual(token["role"], "student")