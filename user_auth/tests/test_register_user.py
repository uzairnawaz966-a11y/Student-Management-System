import uuid
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from user_auth.models import AccountActivationToken
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
    
    def test_registeration_fails_without_password(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_fails_without_username(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_registration_fails_without_email(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_with_extra_field(self):
        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "uzair123",
            "email": "uzair@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123",
            "random_field": "random_value"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registeration_duplicate_email_case_insensitive(self):
        User.objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="testpass123"
        )

        payload = {
            "first_name": "Uzair",
            "last_name": "Nawaz",
            "username": "newuser",
            "email": "TEST@example.com",
            "password": "testpass123",
            "password_confirmation": "testpass123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 201)


class ActivateAccountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="test123",
            is_active=False
        )
        self.activation_token = AccountActivationToken.objects.create(
            user=self.user,
            expiration_date=timezone.now() + timedelta(hours=24)
        )
        self.url = reverse("activate_account", kwargs={"token": self.activation_token.token})

    def test_activate_account_success(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.activation_token.refresh_from_db()

        self.assertTrue(self.user.is_active)
        self.assertTrue(self.activation_token.is_used)

    def test_activation_token_cannot_be_reused(self):

        self.client.post(self.url)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Expired links cannot be used", str(response.data))


    def test_activation_fails_for_expired_token(self):

        self.activation_token.expiration_date = timezone.now() - timedelta(hours=1)
        self.activation_token.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Expired links", str(response.data))

    def test_activation_fails_for_invalid_token(self):
        url = reverse("activate_account", kwargs={"token": uuid.uuid4()})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_user_status_changes_to_active(self):

        self.assertFalse(self.user.is_active)

        self.client.post(self.url)

        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)


    def test_token_is_marked_used_after_activation(self):

        self.assertFalse(self.activation_token.is_used)

        self.client.post(self.url)

        self.activation_token.refresh_from_db()

        self.assertTrue(self.activation_token.is_used)


    def test_token_expiration_date_updated_after_use(self):

        old_expiry = self.activation_token.expiration_date

        self.client.post(self.url)

        self.activation_token.refresh_from_db()

        self.assertNotEqual(old_expiry, self.activation_token.expiration_date)

    def test_activation_for_already_active_user(self):

        self.user.is_active = True
        self.user.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_activation_response_contains_message(self):

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Account activated successfully. You can now login")

    def test_expired_token_returns_message(self):

        self.activation_token.expiration_date = (timezone.now() - timedelta(hours=1))

        self.activation_token.save()

        response = self.client.post(self.url)

        self.assertIn("message", response.data)
    
    def test_used_token_behaves_as_expired(self):

        self.activation_token.is_used = True
        self.activation_token.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)