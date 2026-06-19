from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class LoginAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("jwt_login")

        self.user = User.objects.create_user(
            username="uzair",
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
            "username": "uzair",
            "password": "test123",
            "organization_id": self.org1.id
        }


    def test_login_success(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_login_returns_user_data(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.data["user"]["username"], "uzair")

    def test_login_generates_valid_access_token(self):
        response = self.client.post(self.url, self.payload, format="json")

        token = AccessToken(response.data["tokens"]["access"])

        self.assertEqual(token["organization_id"], self.org1.id)
        self.assertEqual(token["role"], "admin")

    def test_login_case_sensitive_username_behavior(self):
        self.payload["username"] = "UZAIR"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_login_uses_correct_membership(self):
        self.payload["organization_id"] = self.org2.id

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)

        token = AccessToken(response.data["tokens"]["access"])

        self.assertEqual(token["organization_id"], self.org2.id)
        self.assertEqual(token["role"], "student")


    def test_wrong_password_fails(self):
        self.payload["password"] = "wrongpass"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("tokens", response.data)

    def test_wrong_organization_fails(self):
        self.payload["organization_id"] = 999999

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_missing_membership_fails(self):
        Membership.objects.all().delete()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_inactive_user_fails(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_user_fails(self):
        self.payload["username"] = "fakeuser"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)


    def test_missing_username(self):
        payload = self.payload.copy()
        payload.pop("username")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        payload = self.payload.copy()
        payload.pop("password")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_missing_organization(self):
        payload = self.payload.copy()
        payload.pop("organization_id")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_response_structure_consistency(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertIn("tokens", response.data)
        self.assertIn("user", response.data)