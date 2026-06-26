from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership, OrganizationJoinLink
from django.urls import reverse




User = get_user_model()


class RetrieveInviteLinkAPIViewTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="testuser@123"
        )
        self.invited_user = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testuser@123"
        )
        self.org = Organization.objects.create(
            name="ENIGMATIX",
            owner=self.owner
        )
        self.owner_membership = Membership.objects.create(
            user=self.owner,
            organization=self.org,
            role=Membership.Role.OWNER
        )
        self.invite_link = OrganizationJoinLink.objects.create(
            organization=self.org,
            created_by=self.owner_membership,
            role=Membership.Role.STUDENT,
            allowed_emails=["student@test.com"],
            max_users=5
        )
        self.url = reverse(
            "register-invite",
            args=[self.invite_link.token]
        )


    def test_existing_user_is_added_to_organization(self):
        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Membership.objects.filter(
                user=self.invited_user,
                organization=self.org
            ).exists()
        )

        self.assertEqual(response.data["next_step"], "login")

    def test_used_count_increments_when_membership_created(self):
        self.client.post(self.url, {"email": "student@test.com"})

        self.invite_link.refresh_from_db()

        self.assertEqual(self.invite_link.used_count, 1)

    def test_existing_membership_does_not_increment_count_again(self):
        Membership.objects.create(
            user=self.invited_user,
            organization=self.org,
            role=Membership.Role.STUDENT
        )

        self.client.post(self.url, {"email": "student@test.com"})

        self.invite_link.refresh_from_db()

        self.assertEqual(self.invite_link.used_count, 0)

    def test_email_not_in_allowed_emails_returns_400(self):

        response = self.client.post(self.url, {"email": "hacker@test.com"})

        self.assertEqual(response.status_code, 400)

    def test_disabled_link_returns_400(self):
        self.invite_link.status = (OrganizationJoinLink.Status.DISABLED)
        self.invite_link.save()

        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 400)

    def test_usage_limit_reached_returns_400(self):
        self.invite_link.used_count = 5
        self.invite_link.save()

        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 400)
    
    def test_missing_email_returns_400(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
    
    def test_invalid_email_returns_400(self):
        response = self.client.post(self.url, {"email": "not-an-email"})

        self.assertEqual(response.status_code, 400)
    
    def test_new_user_receives_signup_next_step(self):
        self.invite_link.allowed_emails = ["newuser@test.com"]
        self.invite_link.save()

        response = self.client.post(self.url, {"email": "newuser@test.com"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["email_exists"])
        self.assertEqual(response.data["next_step"], "signup")
    
    def test_response_contains_invite_details(self):
        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 200)

        self.assertIn("invite", response.data)
        self.assertIn("organization_name", response.data["invite"])
        self.assertIn("creator", response.data["invite"])
        self.assertIn("status", response.data["invite"])
