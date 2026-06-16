from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from organization.models import Organization, Membership, OrganizationJoinLink
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_token(user, membership):
    refresh = RefreshToken.for_user(user)
    refresh["organization_id"] = membership.organization.id
    refresh["role"] = membership.role
    return str(refresh.access_token)

class OrganizationJoinLinkViewSetTests(APITestCase):

    def setUp(self):
        self.owner_user = User.objects.create_user(
            username="owner",
            password="testuser@123"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            password="testuser@123"
        )
        self.instructor_user = User.objects.create_user(
            username="instructor",
            password="testuser@123"
        )
        self.student_user = User.objects.create_user(
            username="student",
            password="testuser@123"
        )
        self.org = Organization.objects.create(
            name="ENIGMATIX",
            owner=self.owner_user
        )
        self.owner_membership = Membership.objects.create(
            user=self.owner_user,
            organization=self.org,
            role=Membership.Role.OWNER,
            is_active=True
        )
        self.other_one_org = Organization.objects.create(
            name="OTHER ORG",
            owner=self.owner_user
        )
        self.other_one_membership = Membership.objects.create(
            user=self.owner_user,
            organization=self.other_one_org,
            role=Membership.Role.OWNER,
            is_active=True
        )
        self.admin_membership = Membership.objects.create(
            user=self.admin_user,
            organization=self.org,
            role=Membership.Role.ADMIN,
            is_active=True
        )
        self.instructor_membership = Membership.objects.create(
            user=self.instructor_user,
            organization=self.org,
            role=Membership.Role.INSTRUCTOR,
            is_active=True
        )
        self.student_membership = Membership.objects.create(
            user=self.student_user,
            organization=self.org,
            role=Membership.Role.STUDENT,
            is_active=True
        )
        self.list_url = reverse("join-link-list")
        self.create_url = reverse("join-link-list")

    def test_unauthenticated_user_cannot_access_join_links(self):

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)
    
    def test_owner_can_create_join_link(self):

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "role": "STUDENT",
            "max_users": 10
        }

        response = self.client.post(self.create_url, payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("invite_link", response.data)

    def test_admin_can_create_join_link(self):

        token = get_token(self.admin_user, self.admin_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "role": "INSTRUCTOR",
            "max_users": 5
        }

        response = self.client.post(self.create_url, payload)

        self.assertEqual(response.status_code, 201)

    def test_student_cannot_create_join_link(self):

        token = get_token(self.student_user, self.student_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "role": "STUDENT",
            "max_users": 10
        }

        response = self.client.post(self.create_url, payload)

        self.assertEqual(response.status_code, 403)
    
    def test_owner_can_list_join_links(self):

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_list_join_links(self):

        token = get_token(self.student_user, self.student_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)
    
    def test_owner_can_disable_join_link(self):

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.client.post(self.create_url, {
            "role": "STUDENT",
            "max_users": 10
        })

        link_id = OrganizationJoinLink.objects.first().id

        url = reverse("join-link-disable", args=[link_id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Invite link disabled successfully")

    def test_owner_cannot_create_join_link_for_invalid_role(self):

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "role": "OWNER",
            "max_users": 10
        }

        response = self.client.post(self.create_url, payload)

        self.assertEqual(response.status_code, 400)
    
    def test_instructor_cannot_create_join_link(self):


        token = get_token(self.instructor_user, self.instructor_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        payload = {
            "role": "STUDENT",
            "max_users": 10
        }

        response = self.client.post(self.create_url, payload)

        self.assertEqual(response.status_code, 403)
    
    def test_user_cannot_see_join_links_of_another_organization(self):
        OrganizationJoinLink.objects.create(
            organization=self.other_one_org,
            created_by=self.other_one_membership,
            role="STUDENT",
            max_users=5
        )

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.list_url)

        self.assertEqual(len(response.data), 0)

    def test_disable_non_existent_join_link_returns_404(self):

        token = get_token(self.owner_user, self.owner_membership)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("join-link-disable", args=[99999])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)