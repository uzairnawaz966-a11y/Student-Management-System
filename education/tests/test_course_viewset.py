# from rest_framework.test import APITestCase
# from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
# from education.models import Course, Lesson, Enrollment, CourseType, Feedback
# from organization.models import Organization, Membership
# from django.contrib.auth import get_user_model

# User = get_user_model()


def get_token(user, membership):
    refresh = RefreshToken.for_user(user)

    refresh["organization_id"] = membership.organization.id
    refresh["role"] = membership.role

    return str(refresh.access_token)


# class CourseViewSetTests(APITestCase):

#     def authenticate(self, user, membership):
#         token = get_token(user, membership)

#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


#     def setUp(self):

#         self.owner_user = User.objects.create_user(
#             username="owner",
#             password="testuser@123"
#         )

#         self.second_owner_user = User.objects.create_user(
#             username="second owner",
#             password="testuser@123"
#         )

#         self.admin_user = User.objects.create_user(
#             username="admin",
#             password="testuser@123"
#         )

#         self.instructor_user = User.objects.create_user(
#             username="instructor",
#             password="testuser@123"
#         )

#         self.second_instructor_user = User.objects.create_user(
#             username="second instructor",
#             password="testuser@123"
#         )

#         self.student_user = User.objects.create_user(
#             username="student",
#             password="testuser@123"
#         )

#         self.second_student_user = User.objects.create_user(
#             username="second student",
#             password="testuser@123"
#         )

#         self.new_student_user = User.objects.create_user(
#             username="new student",
#             password="testuser@123"
#         )

#         self.non_enrolled_student_user = User.objects.create_user(
#             username="non_enrolled_student",
#             password="testuser@123"
#         )

#         self.org = Organization.objects.create(
#             name="ENIGMATIX",
#             owner=self.owner_user
#         )

#         self.second_org = Organization.objects.create(
#             name="Second Organization",
#             owner=self.second_owner_user
#         )

#         self.owner_membership = Membership.objects.create(
#             user=self.owner_user,
#             organization=self.org,
#             role=Membership.Role.OWNER,
#             is_active=True
#         )

#         self.second_owner_membership = Membership.objects.create(
#             user=self.second_owner_user,
#             organization=self.second_org,
#             role=Membership.Role.OWNER,
#             is_active=True
#         )

#         self.admin_membership = Membership.objects.create(
#             user=self.admin_user,
#             organization=self.org,
#             role=Membership.Role.ADMIN,
#             is_active=True
#         )

#         self.instructor_membership = Membership.objects.create(
#             user=self.instructor_user,
#             organization=self.org,
#             role=Membership.Role.INSTRUCTOR,
#             is_active=True
#         )

#         self.second_instructor_membership = Membership.objects.create(
#             user=self.second_instructor_user,
#             organization=self.second_org,
#             role=Membership.Role.INSTRUCTOR,
#             is_active=True
#         )

#         self.student_membership = Membership.objects.create(
#             user=self.student_user,
#             organization=self.org,
#             role=Membership.Role.STUDENT,
#             is_active=True
#         )

#         self.second_student_membership = Membership.objects.create(
#             user=self.second_student_user,
#             organization=self.org,
#             role=Membership.Role.STUDENT,
#             is_active=True
#         )

#         self.new_student_membership = Membership.objects.create(
#             user=self.new_student_user,
#             organization=self.org,
#             role=Membership.Role.STUDENT,
#             is_active=True
#         )

#         self.non_enrolled_student_membership = Membership.objects.create(
#             user=self.non_enrolled_student_user,
#             organization=self.org,
#             role=Membership.Role.STUDENT,
#             is_active=True
#         )

#         self.course_type = CourseType.objects.create(
#             name="Math"
#         )

#         self.course = Course.objects.create(
#             title="Math Course",
#             description="abcd",
#             organization=self.org,
#             type=self.course_type,
#             instructor=self.instructor_membership,
#             is_active=True,
#             status=Course.Status.PUBLISHED
#         )

#         self.second_course = Course.objects.create(
#             title="Second Course",
#             description="Should not appear",
#             organization=self.second_org,
#             type=self.course_type,
#             instructor=self.second_instructor_membership,
#             is_active=True,
#             status=Course.Status.PUBLISHED
#         )

#         self.draft_course = Course.objects.create(
#             title="Draft Course",
#             description="Draft",
#             organization=self.org,
#             type=self.course_type,
#             instructor=self.instructor_membership,
#             is_active=True,
#             status=Course.Status.DRAFT
#         )

#         self.second_draft_course = Course.objects.create(
#             title="Second Draft",
#             description="Another Course",
#             organization=self.second_org,
#             type=self.course_type,
#             instructor=self.second_instructor_membership,
#             is_active=True,
#             status=Course.Status.DRAFT
#         )

#         self.empty_course = Course.objects.create(
#             title="Empty Course",
#             description="No lessons",
#             organization=self.org,
#             type=self.course_type,
#             instructor=self.instructor_membership,
#             is_active=True,
#             status=Course.Status.DRAFT
#         )

#         self.no_enrollment_course = Course.objects.create(
#             title="No enrollment course",
#             description="No enrollments",
#             organization=self.org,
#             type=self.course_type,
#             instructor=self.instructor_membership,
#             is_active=True,
#             status=Course.Status.PUBLISHED
#         )

#         self.lesson = Lesson.objects.create(
#             title="Algebric Expressions",
#             course=self.course,
#             content="abcd",
#             video_link="http://test.com/video/",
#             order=1,
#             status=Lesson.Status.PUBLISHED
#         )

#         self.draft_course_lesson = Lesson.objects.create(
#             title="Draft course lesson 1",
#             course=self.draft_course,
#             content="abcdefghijklmnpqrstuvwxyz",
#             video_link="http://test.com/video/",
#             order=1,
#             status=Lesson.Status.DRAFT
#         )

#         self.second_draft_course_lesson = Lesson.objects.create(
#             title="Second draft course lesson 1",
#             course=self.second_draft_course,
#             content="abcdefghijklmnpqrstuvwxyz",
#             video_link="http://test.com/video/",
#             order=1,
#             status=Lesson.Status.DRAFT
#         )

#         self.enrollment = Enrollment.objects.create(
#             student=self.student_membership,
#             organization=self.org,
#             course=self.course
#         )

#         self.new_student_enrollment = Enrollment.objects.create(
#             student=self.new_student_membership,
#             organization=self.org,
#             course=self.course
#         )

#         self.approved_feedback = Feedback.objects.create(
#             organization=self.org,
#             student=self.student_membership,
#             course=self.course,
#             rating=5,
#             comment="Excellent course",
#             is_approved=True
#         )

#         self.pending_feedback = Feedback.objects.create(
#             organization=self.org,
#             student=self.second_student_membership,
#             course=self.course,
#             rating=1,
#             comment="Pending",
#             is_approved=False
#         )


#     def test_student_can_access_lessons_endpoint(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-lessons", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["title"], "Algebric Expressions")
#         # 


# # # ----------------------- COURSE CREATION TEST CASES -----------------------

#     def test_owner_can_create_course(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = "/api/v1/course/"

#         data = {
#             "title": "Owner Course",
#             "description": "Created by owner",
#             "instructor_id": self.instructor_membership.id,
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 201)

#         self.assertIn("id", response.data)

#         course = Course.objects.get(id=response.data["id"])

#         self.assertEqual(course.title, "Owner Course")
#         self.assertEqual(course.description, "Created by owner")
#         self.assertEqual(course.instructor, self.instructor_membership)


#     def test_admin_cannot_create_course(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = "api/v1/course/"

#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 404)
#         self.assertFalse(Course.objects.filter(title="Physics").exists())
#         self.assertFalse(Course.objects.filter(description="Basic Physics").exists())


#     def test_instructor_can_create_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = "/api/v1/course/"
        
#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         course_id = response.data["id"]
#         course = Course.objects.get(id=course_id)

#         self.assertIn("id", response.data)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data["title"], "Physics")
#         self.assertEqual(response.data["description"], "Basic Physics")
#         self.assertEqual(response.data["type"], self.course_type.id)
#         self.assertEqual(response.data["is_active"], True)
#         self.assertEqual(course.title, "Physics")
#         self.assertEqual(course.instructor, self.instructor_membership)


#     def test_student_cannot_create_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = "api/v1/course/"

#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 404)
#         self.assertFalse(Course.objects.filter(title="Physics").exists())
#         self.assertFalse(Course.objects.filter(description="Basic Physics").exists())

#     def test_unauthorized_user_cannot_create_course(self):
#         url = "/api/v1/course/"

#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 401)

#     def test_course_creation_fails_without_required_field(self):
#         token = get_token(
#             self.owner_user,
#             self.owner_membership
#         )
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

#         url = "/api/v1/course/"

#         data = {
#             "description": "Basic Physics",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("title", response.data)


#     def test_instructor_cannot_assign_another_instructor_for_course_creation(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = "/api/v1/course/"

#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "instructor_id": self.second_instructor_membership.id,
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(Course.objects.filter(title="Physics").exists())

#     def test_course_creation_failed_with_invalid_type(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = "/api/v1/course/"

#         data = {
#             "title": "Physics",
#             "description": "Basic Physics",
#             "type": 9999,
#             "is_active": True
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(Course.objects.filter(title="Physics").exists())

# # # ----------------------- COURSE LIST TEST CASES -----------------------

#     def test_owner_can_list_courses(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = "/api/v1/course/"

#         response = self.client.get(url)

#         # response.data = [
#         #     {
#         #         'id': 3,
#         #         'organization': 1,
#         #         'title': 'Draft Course',
#         #         'description': 'Draft',
#         #         'type': 1,
#         #         'is_active': True,
#         #         'status': 'DRAFT',
#         #         'published_at': None
#         #     },
#         #     {
#         #         'id': 1,
#         #         'organization': 1,
#         #         'title': 'Math Course',
#         #         'description': 'abcd',
#         #         'type': 1,
#         #         'is_active': True,
#         #         'status': 'PUBLISHED',
#         #         'published_at': None
#         #     }
#         # ]

#         course_data = next((item for item in response.data if item["id"] == self.course.id), None)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(course_data["id"], self.course.id)
#         self.assertEqual(course_data["title"], "Math Course")
#         self.assertEqual(course_data["type"], self.course_type.id)
#         self.assertEqual(course_data["status"], Course.Status.PUBLISHED)

#         course = Course.objects.get(id=self.course.id)

#         self.assertEqual(course.title, "Math Course")
#         self.assertEqual(course.organization, self.org)
#         self.assertEqual(course.instructor, self.instructor_membership)

#     def test_instructor_can_list_courses(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = "/api/v1/course/"

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         course_data = next((item for item in response.data if item["id"] == self.course.id), None)

#         self.assertEqual(course_data["id"], self.course.id)
#         self.assertEqual(course_data["title"], "Math Course")
#         self.assertEqual(course_data["type"], self.course_type.id)
#         self.assertEqual(course_data["status"], Course.Status.PUBLISHED)

#         course = Course.objects.get(id=self.course.id)

#         self.assertEqual(course.title, "Math Course")
#         self.assertEqual(course.organization, self.org)
#         self.assertEqual(course.instructor, self.instructor_membership)


#     def test_admin_can_list_courses(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = "/api/v1/course/"

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         course_data = next((item for item in response.data if item["id"] == self.course.id), None)

#         self.assertEqual(course_data["id"], self.course.id)
#         self.assertEqual(course_data["title"], self.course.title)
#         self.assertEqual(course_data["type"], self.course_type.id)


#     def test_student_can_list_courses(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-list")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         course_data = response.data[0]

#         self.assertEqual(course_data["id"], self.course.id)
#         self.assertEqual(course_data["title"], self.course.title)
#         self.assertEqual(course_data["type"], self.course.type.id)

#     def test_unauthenticated_user_cannot_list_courses(self):
#         url = "/api/v1/course/"

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_user_only_sees_courses_of_current_organization(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-list")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)        
#         self.assertEqual(len(response.data), 2)


# # # ----------------------- COURSE RETRIEVE TEST CASES -----------------------

#     def test_owner_can_retrieve_course(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.data["title"], self.course.title)
#         self.assertEqual(response.data["description"], self.course.description)
#         self.assertEqual(response.data["type"], self.course.type.id)

#     def test_admin_can_retrieve_course(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.data["title"], self.course.title)
#         self.assertEqual(response.data["description"], self.course.description)
#         self.assertEqual(response.data["type"], self.course.type.id)

#     def test_instructor_can_retrieve_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )
        
#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.data["title"], self.course.title)
#         self.assertEqual(response.data["description"], self.course.description)
#         self.assertEqual(response.data["type"], self.course.type.id)

#     def test_student_can_retrieve_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.data["title"], self.course.title)
#         self.assertEqual(response.data["description"], self.course.description)
#         self.assertEqual(response.data["type"], self.course.type.id)

#     def test_unauthorized_user_cannot_retrieve_course(self):
#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_user_cannot_retrieve_course_from_another_organization(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-detail", args=[self.second_course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

#     def test_non_existing_course_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[9999])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)


# # ----------------------- COURSE UPDATE TEST CASES -----------------------

#     def test_published_course_cannot_be_updated(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.course.id])

#         data = {
#             "title": "Updated Title"
#         }

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, 400)

#         self.assertIn("You cannot update an already published course", str(response.data))

#         self.course.refresh_from_db()

#         self.assertEqual(self.course.title, "Math Course")

#     def test_owner_can_update_draft_courses(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "title": "Updated Course",
#             "description": "Updated Description",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.put(url, data)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 200)

#         self.assertEqual(self.draft_course.title, "Updated Course")
#         self.assertEqual(self.draft_course.description, "Updated Description")
#         self.assertEqual(self.draft_course.is_active, True)
#         self.assertEqual(self.draft_course.status, Course.Status.DRAFT)

#     def test_admin_cannot_update_draft_course(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "title": "Admin Updated",
#             "description": "Updated by admin",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.put(url, data)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 403)

#     def test_instructor_can_update_own_draft_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "title": "Instructor Updated",
#             "description": "Updated by instructor",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.put(url, data)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.draft_course.title, "Instructor Updated")
#         self.assertEqual(self.draft_course.description, "Updated by instructor")

#     def test_student_cannot_update_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "title": "Updated Title"
#         }

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, 404)

#     def test_unauthorized_user_cannot_update_course(self):

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "title": "Updated Title"
#         }

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, 401)

#     def test_instructor_cannot_update_another_instructor_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-detail", args=[self.second_draft_course.id])

#         data = {
#             "title": "Illegal Update"
#         }

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, 404)

#     def test_user_cannot_update_course_from_another_organization(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.second_draft_course.id])

#         data = {
#             "title": "Illegal Update"
#         }

#         response = self.client.patch(url, data)

#         self.assertEqual(response.status_code, 404)

#     def test_course_update_fails_with_invalid_data(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         data = {
#             "description": "Updated Description",
#             "type": self.course_type.id,
#             "is_active": True
#         }

#         response = self.client.put(url, data)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("title", response.data)

# # ----------------------- COURSE DELETE TEST CASES -----------------------

#     def test_owner_can_delete_draft_courses(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )
#         url = reverse("course-detail", args=[self.draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 204)
#         self.assertFalse(Course.objects.filter(id=self.draft_course.id).exists())

#     def test_admin_cannot_delete_course(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 403)

#         self.assertTrue(Course.objects.filter(id=self.draft_course.id))

#     def test_instructor_can_delete_own_draft_courses(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 204)

#         self.assertFalse(Course.objects.filter(id=self.draft_course.id).exists())

#     def test_student_cannot_delete_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-detail", args=[self.draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 404)

#         self.assertTrue(
#             Course.objects.filter(id=self.draft_course.id).exists()
#         )

#     def test_unauthorized_user_cannot_delete_course(self):

#         url = reverse("course-detail", args=[self.draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 401)

#         self.assertTrue(
#             Course.objects.filter(id=self.draft_course.id).exists()
#         )

#     def test_instructor_cannot_delete_another_instructor_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-detail", args=[self.second_draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 404)

#         self.assertTrue(
#             Course.objects.filter(id=self.second_draft_course.id).exists()
#         )

#     def test_user_cannot_delete_course_from_another_organization(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.second_draft_course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 404)

#         self.assertTrue(
#             Course.objects.filter(id=self.second_draft_course.id).exists()
#         )

#     def test_published_course_cannot_be_deleted(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[self.course.id])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 400)

#         self.assertTrue(
#             Course.objects.filter(id=self.course.id).exists()
#         )

#     def test_non_existing_course_delete_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-detail", args=[9999])

#         response = self.client.delete(url)

#         self.assertEqual(response.status_code, 404)

# # ----------------------- COURSE PUBLISH TEST CASES -----------------------

#     def test_owner_can_publish_draft_course(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["message"], "Course published successfully")
#         self.assertEqual(self.draft_course.status, Course.Status.PUBLISHED)


#     def test_admin_cannot_publish_draft_course(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 403)
#         self.assertEqual(self.draft_course.status, Course.Status.DRAFT)

#     def test_instructor_can_publish_own_draft_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.draft_course.refresh_from_db()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.draft_course.status, Course.Status.PUBLISHED)

#     def test_instructor_cannot_publish_other_instructor_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-publish", args=[self.second_draft_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)
#         self.assertIn("No Course matches the given query.", str(response.data))


#     def test_cannot_publish_course_without_lessons(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-publish", args=[self.empty_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("Course cannot be published without any lesson", str(response.data))

#     def test_cannot_publish_already_published_course(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-publish", args=[self.course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("Only draft courses can be published", str(response.data))


#     def test_student_cannot_publish_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)


#     def test_unauthenticated_user_cannot_publish_course(self):
#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 401)


#     def test_user_from_another_org_cannot_publish_course(self):
#         self.authenticate(
#             self.second_owner_user,
#             self.second_owner_membership
#         )

#         url = reverse("course-publish", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)


#     def test_publish_non_existent_course_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-publish", args=[99999])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)

# # ----------------------- COURSE CREATE LESSON TEST CASES -----------------------

#     def test_instructor_can_create_lesson_for_own_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "Lesson 1",
#             "content": "Some content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(Lesson.objects.filter(title="Lesson 1", course=self.draft_course).exists())

#     def test_owner_can_create_lesson(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "Owner Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 201)
#         self.assertTrue(Lesson.objects.filter(title="Owner Lesson").exists())

#     def test_admin_cannot_create_lesson(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "Admin Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 403)
#         self.assertFalse(Lesson.objects.filter(title="Admin Lesson").exists())

#     def test_student_cannot_create_lesson(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "Student Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#         }

#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 404)

#     def test_instructor_cannot_create_lesson_for_other_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-create-lesson", args=[self.second_draft_course.id])

#         data = {
#             "title": "Illegal Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 404)
#         self.assertFalse(Lesson.objects.filter(title="Illegal Lesson").exists())

#     def test_unauthenticated_user_cannot_create_lesson(self):
#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "No Auth Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 401)

#     def test_create_lesson_invalid_course_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-create-lesson", args=[99999])

#         data = {
#             "title": "Invalid Course Lesson",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 404)

#     def test_create_lesson_missing_required_fields(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "content": "Missing title",
#             "video_link": "http://test.com/video/",
#             "order": 1
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("title", response.data)

#     def test_lesson_is_saved_with_correct_course(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-create-lesson", args=[self.draft_course.id])

#         data = {
#             "title": "Relation Test",
#             "content": "Content",
#             "video_link": "http://test.com/video/",
#             "order": 2
#         }

#         self.client.post(url, data)

#         lesson = Lesson.objects.get(title="Relation Test")

#         self.assertEqual(lesson.course, self.draft_course)

# # ----------------------- COURSE LESSONS LIST TEST CASES -----------------------

#     def test_student_sees_only_published_lessons(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-lessons", args=[self.course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["title"], self.lesson.title)

#     def test_non_enrolled_student_cannot_see_content(self):
#         self.authenticate(
#             self.non_enrolled_student_user,
#             self.non_enrolled_student_membership
#         )

#         url = reverse("course-lessons", args=[self.course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         lesson = response.data[0]

#         self.assertNotIn("content", lesson)
#         self.assertNotIn("video_link", lesson)
    
#     def test_enrolled_student_sees_full_lesson_data(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-lessons", args=[self.course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#         lesson = response.data[0]

#         self.assertIn("content", lesson)
#         self.assertIn("video_link", lesson)

#     def test_instructor_sees_own_course_all_lessons(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-lessons", args=[self.draft_course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertGreaterEqual(len(response.data), 1)
    
#     def test_instructor_cannot_access_other_instructor_lessons(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-lessons", args=[self.second_course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)
    
#     def test_owner_sees_all_lessons_with_full_data(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-lessons", args=[self.draft_course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertGreaterEqual(len(response.data), 1)

#         lesson = response.data[0]
#         self.assertIn("content", lesson)
#         self.assertIn("video_link", lesson)

#     def test_admin_sees_all_lessons(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-lessons", args=[self.course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
    
#     def test_cross_org_access_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-lessons", args=[self.second_course.id])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

#     def test_unauthenticated_user_cannot_access_lessons(self):
#         url = reverse("course-lessons", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_invalid_course_returns_404(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-lessons", args=[99999])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

# # ----------------------- COURSE ENROLL TEST CASES -----------------------

#     def test_student_can_enroll_in_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-enroll", args=[self.no_enrollment_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data["message"], "You are enrolled successfully")

#         self.assertTrue(Enrollment.objects.filter(student=self.student_membership, course=self.course).exists())

#     def test_student_cannot_enroll_twice(self):
#         self.authenticate(self.student_user, self.student_membership)

#         url = reverse("course-enroll", args=[self.course.id])

#         self.client.post(url)
#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 400)
#         self.assertIn("Already enrolled", str(response.data))

#     def test_unauthenticated_user_cannot_enroll(self):
#         url = reverse(
#             "course-enroll",
#             args=[self.no_enrollment_course.id]
#         )

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 401)

#     def test_instructor_cannot_enroll_in_courses(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-enroll", args=[self.course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 403)

#     def test_student_cannot_enroll_in_draft_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-enroll", args=[self.draft_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)
#         self.assertIn("Course not found", response.data["detail"])

#     def test_invalid_course_returns_404(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-enroll", args=[99999])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)

# # ----------------------- COURSE CANCEL ENROLLMENT TEST CASES -----------------------

#     def test_student_can_cancel_enrollment(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-cancel-enrollment", args=[self.course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 204)
#         self.assertIn("Enrollment cancelled", response.data["message"])
#         self.assertFalse(Enrollment.objects.filter(student=self.student_membership, course=self.course).exists())

#     def test_student_cannot_cancel_without_enrollment(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-cancel-enrollment", args=[self.no_enrollment_course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)

#     def test_unauthenticated_user_cannot_cancel_enrollment(self):
#         url = reverse("course-cancel-enrollment", args=[self.course.id])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 401)

#     def test_cancel_enrollment_invalid_course_returns_404(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-cancel-enrollment", args=[99999])

#         response = self.client.post(url)

#         self.assertEqual(response.status_code, 404)

#     def test_enrollment_deleted_after_cancel(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-cancel-enrollment", args=[self.course.id])

#         self.client.post(url)

#         self.assertEqual(Enrollment.objects.filter(student=self.student_membership, course=self.course).count(), 0)

# # ----------------------- COURSE ENROLLMENTS TEST CASES -----------------------

#     def test_owner_can_view_course_enrollments(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-course-enrollments", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#     def test_admin_can_view_course_enrollments(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-course-enrollments", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#     def test_instructor_can_view_course_enrollments(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-course-enrollments", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#     def test_student_cannot_view_course_enrollments(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse(
#             "course-course-enrollments",
#             args=[self.course.id]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 403)

#     def test_unauthenticated_user_cannot_view_course_enrollments(self):
#         url = reverse("course-course-enrollments", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_course_enrollments_returns_all_enrollments(self):
#         Enrollment.objects.create(
#             student=self.second_student_membership,
#             course=self.course,
#             organization_id=self.org.id
#         )

#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-course-enrollments", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 3)
    
#     def test_course_enrollments_invalid_course_returns_404(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-course-enrollments", args=[99999])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

#     def test_user_from_another_organization_cannot_view_course_enrollments(self):
#         self.authenticate(
#             self.second_owner_user,
#             self.second_owner_membership
#         )

#         url = reverse(
#             "course-course-enrollments",
#             args=[self.course.id]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)
    
#     def test_course_enrollment_returns_empty_list_if_no_enrollment_exist(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )
#         url = reverse("course-course-enrollments", args=[self.no_enrollment_course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 0)
    
#     def test_course_enrollments_only_returns_requested_course_enrollments(self):
#         Enrollment.objects.create(
#             student=self.second_student_membership,
#             course=self.no_enrollment_course,
#             organization=self.org
#         )

#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse(
#             "course-course-enrollments",
#             args=[self.course.id]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

# # ----------------------- COURSE GIVE FEEDBACK TEST CASES -----------------------

#     def test_student_can_give_feedback(self):
#         self.authenticate(
#             self.new_student_user,
#             self.new_student_membership
#         )

#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 3,
#             "comment": "This course was good"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data["message"], "Feedback posted")
#         self.assertTrue(Feedback.objects.filter(course=self.course, student=self.new_student_membership).exists())

#     def test_unenrolled_student_cannot_give_feedback(self):
#         self.authenticate(
#             self.non_enrolled_student_user,
#             self.non_enrolled_student_membership
#         )

#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 4,
#             "comment": "Nice course"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 403)

#     def test_instructor_cannot_give_feedback(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 5,
#             "comment": "I am instructor"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 403)

#     def test_admin_cannot_give_feedback(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )
        
#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 5,
#             "comment": "I am admin"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 403)

#     def test_unauthorized_user_cannot_give_feedback(self):
#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 5,
#             "comment": "Unauthorized user is giving feedback"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 401)

#     def test_give_feedback_invalid_course_returns_404(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-feedback", args=[99999])

#         data = {
#             "rating": 5,
#             "comment": "Testing comment"
#         }

#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 404)

#     def test_student_cannot_give_feedback_twice(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )
#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 5,
#             "comment": "Testing"
#         }

#         self.client.post(url, data)
#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 400)

#     def test_feedback_is_linked_correctly(self):
#         self.authenticate(
#             self.new_student_user,
#             self.new_student_membership
#         )

#         url = reverse("course-feedback", args=[self.course.id])

#         data = {
#             "rating": 3,
#             "comment": "Good"
#         }

#         self.client.post(url, data)

#         feedback = Feedback.objects.get(course=self.course, comment="Good")

#         self.assertEqual(feedback.student, self.new_student_membership)
#         self.assertEqual(feedback.course, self.course)
#         self.assertEqual(feedback.rating, 3)
#         self.assertEqual(feedback.comment, "Good")

# # ----------------------- COURSE STUDENT ENROLLMENTS TEST CASES -----------------------

#     def test_student_can_view_own_enrollments(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)

#         enrollment = response.data[0]

#         self.assertEqual(enrollment["course"], self.course.id)

#     def test_student_only_sees_his_own_enrollments(self):
#         Enrollment.objects.create(
#             student=self.second_student_membership,
#             course=self.no_enrollment_course,
#             organization=self.org
#         )

#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)

#         enrollment = response.data[0]

#         self.assertEqual(enrollment["course"], self.course.id)

#     def test_student_with_no_enrollments_gets_empty_list(self):
#         self.authenticate(
#             self.non_enrolled_student_user,
#             self.non_enrolled_student_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 0)

#     def test_unauthenticated_user_cannot_view_my_enrollments(self):
#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_instructor_cannot_view_enrollment_list(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 403)

#     def test_admin_cannot_view_enrollment_list(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 403)

#     def test_owner_cannot_view_enrollment_list(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 403)

#     def test_my_enrollments_are_ordered_by_latest_first(self):
#         Enrollment.objects.create(
#             student=self.student_membership,
#             course=self.no_enrollment_course,
#             organization=self.org
#         )

#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-my-enrollments")

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 2)

#         self.assertEqual(response.data[0]["course"], self.no_enrollment_course.id)

#         self.assertEqual(response.data[1]["course"], self.course.id)

# # ----------------------- COURSE ENROLLMENT STATUS TEST CASES -----------------------

#     def test_enrolled_student_enrollment_status_returns_true(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-enrollment-status", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["course_id"], self.course.id)
#         self.assertTrue(response.data["is_enrolled"])

#     def test_non_enrolled_student_enrollment_status_returns_false(self):
#         self.authenticate(
#             self.non_enrolled_student_user,
#             self.non_enrolled_student_membership
#         )

#         url = reverse("course-enrollment-status", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data["course_id"], self.course.id)
#         self.assertFalse(response.data["is_enrolled"])

#     def test_unauthenticated_user_cannot_check_enrollment_status(self):
#         url = reverse("course-enrollment-status", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_enrollment_status_invalid_course_returns_404(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-enrollment-status", args=[99999])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

# # ----------------------- COURSE FEEDBACKS LIST TEST CASES -----------------------

#     def test_student_can_view_course_feedbacks(self):

#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)

#     def test_instructor_can_view_course_feedbacks(self):
#         self.authenticate(
#             self.instructor_user,
#             self.instructor_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#     def test_admin_can_view_course_feedbacks(self):
#         self.authenticate(
#             self.admin_user,
#             self.admin_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#     def test_owner_can_view_course_feedbacks(self):
#         self.authenticate(
#             self.owner_user,
#             self.owner_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)

#     def test_only_approved_feedbacks_are_returned(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)

#     def test_course_feedbacks_only_return_feedbacks_of_requested_course(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse("course-course-feedbacks", args=[self.course.id])

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data), 1)

#     def test_unauthenticated_user_cannot_view_course_feedbacks(self):
#         url = reverse(
#             "course-course-feedbacks",
#             args=[self.course.id]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 401)

#     def test_course_feedbacks_invalid_course_returns_404(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse(
#             "course-course-feedbacks",
#             args=[99999]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)

#     def test_user_cannot_view_feedbacks_of_course_from_another_organization(self):
#         self.authenticate(
#             self.student_user,
#             self.student_membership
#         )

#         url = reverse(
#             "course-course-feedbacks",
#             args=[self.second_course.id]
#         )

#         response = self.client.get(url)

#         self.assertEqual(response.status_code, 404)