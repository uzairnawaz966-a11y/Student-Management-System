from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from organization.models import Membership, Organization

User = get_user_model()
class JWTLoginTests(APITestCase):

    def setUp(self):
        self.url = reverse("jwt_login")

        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="test123",
            is_active=True
        )

        self.organization = Organization.objects.create(
            name="Test Organization",
            owner=self.user
        )

        self.membership = Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role="admin",
            is_active=True
        )

        self.payload = {
            "username": "uzair",
            "password": "test123",
            "organization_id": self.organization.id
        }

    def test_login_success(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)

        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "uzair")


    def test_login_fails_wrong_password(self):

        self.payload["password"] = "wrongpass"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid credentials", str(response.data))


    def test_login_fails_user_not_found(self):

        self.payload["username"] = "fakeuser"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid organization", str(response.data))


    def test_login_fails_missing_membership(self):

        Membership.objects.all().delete()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid organization", str(response.data))


    def test_login_fails_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("inactive", str(response.data).lower())


    def test_login_fails_wrong_org(self):

        self.payload["organization_id"] = 999

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid organization", str(response.data))


    def test_login_fails_inactive_membership(self):

        self.membership.is_active = False
        self.membership.save()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 400)


    def test_login_response_structure(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertIn("message", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("user", response.data)

        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_jwt_contains_custom_claims(self):

        response = self.client.post(self.url, self.payload, format="json")

        access_token = response.data["tokens"]["access"]

        token = AccessToken(access_token)

        self.assertEqual(token["organization_id"], 1)
        self.assertEqual(token["role"], "admin")

    def test_login_respects_correct_membership(self):

        second_org = Organization.objects.create(
            name="Second Organization",
            owner=self.user
        )

        Membership.objects.create(
            user=self.user,
            organization=second_org,
            role="student",
            is_active=True
        )

        self.payload["organization_id"] = self.organization.id

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["user"]["username"],
            self.user.username
        )


    def test_login_fails_missing_org(self):

        payload = self.payload.copy()
        payload.pop("organization_id")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("organization_id", response.data)