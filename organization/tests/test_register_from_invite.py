from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership, OrganizationJoinLink
from user_auth.models import AccountActivationToken

User = get_user_model()


class RegisterFromInviteAPIViewTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="uzair",
            email="owner@test.com",
            password="testpass123",
            first_name="Uzair",
            last_name="Nawaz"
        )
        self.organization = Organization.objects.create(
            name="ENIGMATIX",
            owner=self.owner
        )
        self.invite_link = OrganizationJoinLink.objects.create(
            organization=self.organization,
            created_by=Membership.objects.create(
                user=self.owner,
                organization=self.organization,
                role=Membership.Role.OWNER,
                is_active=True
            ),
            role=Membership.Role.STUDENT,
            max_users=10
        )
        self.url = reverse("register-invite", args=[self.invite_link.token])

    def test_user_can_register_from_valid_invite_link(self):
        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "hamza@test.com",
            "password": "testuser@123",
            "password_confirmation": "testuser@123"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="hamza")
        self.assertEqual(user.email, "hamza@test.com")

        membership = Membership.objects.get(user=user)
        self.assertEqual(membership.organization, self.organization)
        self.assertEqual(membership.role, Membership.Role.STUDENT)
        self.assertFalse(membership.is_active)

    def test_register_from_invalid_token_returns_404(self):
        url = reverse("register-invite", args=["00000000-0000-0000-0000-000000000000"])

        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "hamza@test.com",
            "password": "testuser@123",
            "password_confirmation": "testuser@123"
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 404)

    def test_register_from_invite_fails_when_passwords_do_not_match(self):
        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "hamza@test.com",
            "password": "testuser@123",
            "password_confirmation": "wrongpass"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)

    def test_register_from_invite_fails_when_email_already_exists(self):
        User.objects.create_user(
            username="existing",
            email="aslam@test.com",
            password="testuser@123",
            first_name="Hamid",
            last_name="Nadeem"
        )

        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "aslam@test.com",
            "password": "testuset@123",
            "password_confirmation": "testuset@123"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)

    def test_register_from_invite_fails_when_username_already_exists(self):
        User.objects.create_user(
            username="hamza",
            email="hamzakhan@test.com",
            password="testuser@123",
            first_name="Hamid",
            last_name="Nadeem"
        )

        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "hamza2@test.com",
            "password": "testuser@123",
            "password_confirmation": "testuser@123"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)

    def test_register_from_invite_creates_inactive_user(self):
        payload = {
            "first_name": "Nasir",
            "last_name": "Mansoor",
            "username": "nasir",
            "email": "nasirmansoor@test.com",
            "password": "testuser@123",
            "password_confirmation": "testuser@123"
        }

        self.client.post(self.url, payload)

        user = User.objects.get(username="nasir")

        self.assertFalse(user.is_active)

    def test_register_from_invite_creates_membership_with_invite_role(self):
        payload = {
            "first_name": "Khalid",
            "last_name": "Ashraf",
            "username": "khalid",
            "email": "khalidashraf@test.com",
            "password": "testuser@123",
            "password_confirmation": "testuser@123"
        }

        self.client.post(self.url, payload)

        user = User.objects.get(username="khalid")
        membership = Membership.objects.get(user=user)

        self.assertEqual(membership.role, Membership.Role.STUDENT)

    def test_register_from_invite_creates_membership_in_invite_organization(self):
        payload = {
            "first_name": "Nasir",
            "last_name": "Mansoor",
            "username": "nasir",
            "email": "nasirmansoor@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        self.client.post(self.url, payload)

        user = User.objects.get(username="nasir")
        membership = Membership.objects.get(user=user)

        self.assertEqual(membership.organization, self.organization)

    def test_register_from_invite_creates_activation_token(self):
        payload = {
            "first_name": "Nasir",
            "last_name": "Mansoor",
            "username": "nasir",
            "email": "nasirmansoor@test.com",
            "password": "testpass123",
            "password_confirmation": "testpass123"
        }

        self.client.post(self.url, payload)

        user = User.objects.get(username="nasir")

        token_exists = AccountActivationToken.objects.filter(user=user).exists()
        self.assertTrue(token_exists)

    def test_register_from_invite_without_password_confirmation_returns_400(self):
        payload = {
            "first_name": "Hamza",
            "last_name": "Khan",
            "username": "hamza",
            "email": "hamzakhan@test.com",
            "password": "testuser@123"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 400)