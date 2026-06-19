from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from user_auth.services.auth_service import EmailClient
from user_auth.services.auth_service import AuthService
from user_auth.models import AccountActivationToken

User = get_user_model()


class AuthServiceResendActivationEdgeCases(TestCase):

    def setUp(self):
        self.service = AuthService()

        self.user = User.objects.create_user(
            username="uzair",
            email="uzair@test.com",
            password="test123",
            is_active=False
        )

        self.active_user = User.objects.create_user(
            username="active",
            email="active@test.com",
            password="test123",
            is_active=True
        )

    def test_resend_activation_empty_email(self):
        response, status_code = self.service.resend_activation_link("")

        self.assertEqual(status_code, 404)

    def test_resend_activation_none_email(self):
        response, status_code = self.service.resend_activation_link(None)

        self.assertEqual(status_code, 404)

    def test_resend_activation_user_not_found(self):
        response, status_code = self.service.resend_activation_link("fake@test.com")

        self.assertEqual(status_code, 404)
        self.assertIn("does not exist", response["message"].lower())

    def test_resend_activation_active_user(self):
        response, status_code = self.service.resend_activation_link(self.active_user.email)

        self.assertEqual(status_code, 400)
        self.assertIn("already activated", response["message"].lower())

    def test_resend_creates_token_for_user(self):
        response, status_code = self.service.resend_activation_link(self.user.email)

        self.assertEqual(status_code, 200)

        self.assertTrue(
            AccountActivationToken.objects.filter(user=self.user).exists()
        )

    def test_resend_reuses_existing_token_if_not_expired(self):
        AccountActivationToken.objects.create(
            user=self.user,
            expiration_date=timezone.now() + timedelta(hours=5)
        )

        response, status_code = self.service.resend_activation_link(self.user.email)

        self.assertEqual(status_code, 200)

        self.assertEqual(
            AccountActivationToken.objects.filter(user=self.user).count(),
            1
        )

    def test_resend_recreates_token_if_expired(self):
        AccountActivationToken.objects.create(
            user=self.user,
            expiration_date=timezone.now() - timedelta(hours=1)
        )

        response, status_code = self.service.resend_activation_link(self.user.email)

        self.assertEqual(status_code, 200)

        self.assertEqual(
            AccountActivationToken.objects.filter(user=self.user).count(),
            1
        )

    def test_resend_activation_handles_email_failure_gracefully(self):

        original = EmailClient.send_verification_email

        def failing_send(*args, **kwargs):
            raise Exception("SMTP failure")

        EmailClient.send_verification_email = failing_send

        response, status_code = self.service.resend_activation_link(self.user.email)

        self.assertEqual(status_code, 201)

        EmailClient.send_verification_email = original