from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

User = get_user_model()


class TokenRefreshAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("token_refresh")

        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="test123",
            is_active=True
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh["organization_id"] = 10
        self.refresh["role"] = "admin"

        self.valid_refresh = str(self.refresh)


    def test_refresh_token_success(self):
        response = self.client.post(
            self.url,
            {"refresh": self.valid_refresh},
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_access_token_contains_custom_claims(self):
        response = self.client.post(
            self.url,
            {"refresh": self.valid_refresh},
            format="json"
        )

        access = response.data["access"]
        decoded = AccessToken(access)

        self.assertEqual(decoded["organization_id"], 10)
        self.assertEqual(decoded["role"], "admin")

    def test_refresh_does_not_break_on_valid_input(self):
        response = self.client.post(
            self.url,
            {"refresh": self.valid_refresh},
            format="json"
        )

        self.assertIsInstance(response.data, dict)


    def test_invalid_refresh_token(self):
        response = self.client.post(
            self.url,
            {"refresh": "invalid.token.string"},
            format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_malformed_refresh_token(self):
        response = self.client.post(
            self.url,
            {"refresh": "abc"},
            format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_missing_refresh_token(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_null_refresh_token(self):
        response = self.client.post(
            self.url,
            {"refresh": None},
            format="json"
        )

        self.assertEqual(response.status_code, 400)


    def test_refresh_token_without_claims(self):
        plain = RefreshToken.for_user(self.user)

        response = self.client.post(
            self.url,
            {"refresh": str(plain)},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        decoded = AccessToken(response.data["access"])
        self.assertIn("organization_id", decoded)
        self.assertIn("role", decoded)


    def test_response_structure(self):
        response = self.client.post(
            self.url,
            {"refresh": self.valid_refresh},
            format="json"
        )

        self.assertIn("access", response.data)