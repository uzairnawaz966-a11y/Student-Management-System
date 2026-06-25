from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership

User = get_user_model()


class CheckEmailAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testuser@123"
        )
        self.org = Organization.objects.create(
            name="ENIGMATIX",
            owner=self.user
        )
        self.membership = Membership.objects.create(
            user=self.user,
            organization=self.org,
            role=Membership.Role.STUDENT,
            is_active=True
        )

        self.url = reverse("check-email")


    def test_existing_email_returns_joined_organizations(self):
        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["organization_exists"])
        self.assertEqual(len(response.data["Joined organizations"]), 1)
        self.assertEqual(response.data["Joined organizations"][0]["name"], "ENIGMATIX")
    
    def test_non_existing_email_returns_empty_list(self):
        response = self.client.post(self.url, {"email": "unknown@test.com"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["organization_exists"])
        self.assertEqual(response.data["Joined organizations"], [])

    def test_returns_all_joined_organizations(self):
        second_org = Organization.objects.create(
            name="SECOND ORG",
            owner=self.user
        )
        Membership.objects.create(
            user=self.user,
            organization=second_org,
            role=Membership.Role.ADMIN,
            is_active=True
        )
        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["Joined organizations"]), 2)

    def test_invalid_email_returns_400(self):
        response = self.client.post(self.url, {"email": "not-an-email"})

        self.assertEqual(response.status_code, 400)
    
    def test_returns_membership_role(self):
        response = self.client.post(self.url, {"email": "student@test.com"})

        self.assertEqual(response.data["Joined organizations"][0]["role"], Membership.Role.STUDENT)
    
    def test_email_with_no_organizations_returns_empty_list(self):

        response = self.client.post(self.url, {"email": "unknown@test.com"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["organization_exists"])
        self.assertEqual(response.data["Joined organizations"], [])
    
    def test_returns_multiple_organizations(self):
        second_org = Organization.objects.create(
            name="SECOND ORG",
            owner=self.user
        )
        Membership.objects.create(
            user=self.user,
            organization=second_org,
            role=Membership.Role.ADMIN
        )

        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["Joined organizations"]), 2)
    
    def test_invalid_email_returns_400(self):
        response = self.client.post(self.url, {"email": "invalid-email"})

        self.assertEqual(response.status_code, 400)
    
    def test_returns_correct_role(self):
        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["Joined organizations"][0]["role"], Membership.Role.STUDENT)
    
    def test_returns_correct_organization_name(self):
        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["Joined organizations"][0]["name"], self.org.name)