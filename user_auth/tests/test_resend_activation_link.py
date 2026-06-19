# from django.urls import reverse
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class ResendActivationLinkTests(APITestCase):

#     def setUp(self):
#         self.url = reverse("resend_activation_link")

#         self.user = User.objects.create_user(
#             username="uzair",
#             email="uzair@test.com",
#             password="test123",
#             is_active=False
#         )

#         self.active_user = User.objects.create_user(
#             username="activeuser",
#             email="active@test.com",
#             password="test123",
#             is_active=True
#         )


#     def test_resend_activation_link_success(self):
#         payload = {"email": self.user.email}

#         response = self.client.post(self.url, payload, format="json")

#         self.assertEqual(response.status_code, 200)
#         self.assertIn("message", response.data)


#     def test_resend_activation_link_missing_email(self):
#         response = self.client.post(self.url, {}, format="json")

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("Email is required", str(response.data))


#     def test_resend_activation_link_user_not_found(self):
#         payload = {"email": "fake@email.com"}

#         response = self.client.post(self.url, payload, format="json")

#         self.assertEqual(response.status_code, 404)
#         self.assertIn("user does not exist", str(response.data).lower())


#     def test_resend_activation_link_active_user(self):
#         payload = {"email": self.active_user.email}

#         response = self.client.post(self.url, payload, format="json")

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("account already activated", str(response.data).lower())


#     def test_resend_activation_response_structure(self):
#         payload = {"email": self.user.email}

#         response = self.client.post(self.url, payload, format="json")

#         self.assertIn("message", response.data)