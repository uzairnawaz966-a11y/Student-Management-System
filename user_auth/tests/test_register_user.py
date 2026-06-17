from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserTests(APITestCase):

    def setUp(self):
        self.url = reverse("register_user")

    def test_user_registration_success(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(username="uzair123").exists())

        user = User.objects.get(username="uzair123")

        self.assertFalse(user.is_active)

        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "uzair@test.com")

    def test_registration_fails_password_mismatch(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "wrongpass"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords don't match", str(response.data))

    def test_registration_missing_required_fields(self):
        payload = {
            "username": "uzair123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="existing@test.com",
            password="testpass123"
        )

        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "newuser",
            "email": "existing@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        User.objects.create_user(
            username="uzair123",
            email="u1@test.com",
            password="testpass123"
        )

        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "u2@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_password_confirmation(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirmation", response.data)

    def test_no_user_created_on_invalid_payload(self):
        payload = {
            "username": "",
            "email": "invalid-email",
            "password": "123",
            "password_confirmation": "1234"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_registration_fails_invalid_email_format(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "not-an-email",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_registration_fails_empty_strings(self):
        payload = {
            "first_name": "",
            "last_name": "",
            "username": "",
            "email": "",
            "password": "",
            "password_confirmation": ""
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_registration_fails_empty_strings(self):
        payload = {
            "first_name": "",
            "last_name": "",
            "username": "",
            "email": "",
            "password": "",
            "password_confirmation": ""
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_password_length_exceeds_limits(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "x" * 50,
            "password_confirmation": "x" * 50
        }
    
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_user_always_created_as_inactive(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        user = User.objects.get(username="uzair123")

        self.assertFalse(user.is_active)

    def test_response_structure_is_consistent(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertIn("message", response.data)
        self.assertIn("user", response.data)

        self.assertIn("id", response.data["user"])
        self.assertIn("username", response.data["user"])
        self.assertIn("email", response.data["user"])