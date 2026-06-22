from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.url = reverse("change_password")

        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="oldpass123",
            is_active=True
        )

        self.client.force_authenticate(user=self.user)

    # def test_change_password_success(self):
    #     payload = {
    #         "password": "oldpass123",
    #         "new_password": "newpass123"
    #     }
    
    #     response = self.client.post(self.url, payload)

    #     self.assertEqual(response.status_code, 200)
    #     self.user.refresh_from_db()

    #     self.assertTrue(self.user.check_password, "newpass123")
    
    # def test_change_password_missing_old_password(self):
    #     payload = {
    #         "new_password": "newpass123"
    #     }

    #     response = self.client.post(self.url, payload)

    #     self.assertEqual(response.status_code, 400)

    # def test_change_password_missing_new_password(self):
    #     payload = {
    #         "password": "oldpass123"
    #     }

    #     response = self.client.post(self.url, payload)

    #     self.assertEqual(response.status_code, 400)

    def test_change_password_missing_both_passwords(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
    
    def test_change_password_wrong_old_password(self):
        payload = {
            "password": "wrongpass123",
            "new_password": "newpass123"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)
    
    def test_change_password_requires_authentication(self):
        self.client.force_authenticate(user=None)
        payload = {
            "password": "oldpass123",
            "new_password": "newpass123"
        }

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 401)

    def test_old_password_no_longer_works(self):
        payload = {
            "password": "oldpass123",
            "new_password": "newpass123"
        }

        self.client.post(self.url, payload)

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password("oldpass123")
        )


class CustomTokenRefreshTests(APITestCase):
    def setUp(self):
        self.url = reverse("token_refresh")

        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="test123",
            is_active=True
        )

        self.refresh = str(
            RefreshToken.for_user(self.user)
        )

    def test_refresh_token_success(self):
        response = self.client.post(self.url, {"refresh": self.refresh}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
    
    def test_refresh_token_invalid(self):
        response = self.client.post(self.url, {"refresh": "invalid-token"}, format="json")

        self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_missing(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, 400)
    
    def test_change_password_to_same_password(self):
        payload = {
            "password": "oldpass123",
            "new_password": "oldpass123"
        }

        response = self.client.post(self.url, payload)

        self.assertIn(response.status_code, [200, 400])
    
    def test_change_password_empty_strings(self):
        payload = {
            "password": "",
            "new_password": ""
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)
    
    def test_refresh_response_contains_access_token(self):
        response = self.client.post(self.url, {"refresh": self.refresh}, format="json")

        self.assertIn("access", response.data)