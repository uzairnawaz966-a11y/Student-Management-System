from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organization.models import Organization, Membership
from django.urls import reverse

User = get_user_model()

class OrganizationCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="uzair",
            password="testuser@123"
        )

        self.client.force_authenticate(self.user)

        self.url = reverse("organization-create")

        self.valid_payload = {
            "name": "Test Organization",
            "description": "Test Description"
        }

    def test_authenticated_user_can_create_organization(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "Organization created successfully")
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(Membership.objects.count(), 1)

        organization = Organization.objects.first()
        membership = Membership.objects.first()

        self.assertEqual(organization.owner, self.user)
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.organization, organization)

    def test_unauthenticated_user_cannot_create_organization(self):
        self.client.force_authenticate(user=None)
        
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Organization.objects.count(), 0)
        self.assertEqual(Membership.objects.count(), 0)

    def test_organization_creation_needs_name(self):
        payload = {
            "description": "Test Description"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)

        self.assertIn("name", response.data)

    def test_organization_creation_with_empty_name_fails(self):
        payload = {
            "name": "",
            "description": "Test Description"
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("name", response.data)

    def test_organization_cannot_be_created_without_description(self):
        payload = {
            "name": "Test Organization"
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Organization.objects.count(), 0)