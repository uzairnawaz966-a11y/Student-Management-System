from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from education.models import Course, Lesson, Enrollment, CourseType
from organization.models import Organization, Membership
from django.contrib.auth import get_user_model

User = get_user_model()


def get_token(user, membership):
    refresh = RefreshToken.for_user(user)

    refresh["organization_id"] = membership.organization.id
    refresh["role"] = membership.role

    return str(refresh.access_token)


class CourseViewSetTests(APITestCase):

    def authenticate(self, user, membership):
        token = get_token(user, membership)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


    def setUp(self):

        self.owner_user = User.objects.create_user(
            username="owner",
            password="testuser@123"
        )

        self.second_owner_user = User.objects.create_user(
            username="second owner",
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

        self.second_instructor_user = User.objects.create_user(
            username="second instructor",
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

        self.second_org = Organization.objects.create(
            name="Second Organization",
            owner=self.second_owner_user
        )

        self.owner_membership = Membership.objects.create(
            user=self.owner_user,
            organization=self.org,
            role=Membership.Role.OWNER,
            is_active=True
        )

        self.second_owner_membership = Membership.objects.create(
            user=self.second_owner_user,
            organization=self.second_org,
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

        self.second_instructor_membership = Membership.objects.create(
            user=self.second_instructor_user,
            organization=self.second_org,
            role=Membership.Role.INSTRUCTOR,
            is_active=True
        )

        self.student_membership = Membership.objects.create(
            user=self.student_user,
            organization=self.org,
            role=Membership.Role.STUDENT,
            is_active=True
        )

        self.course_type = CourseType.objects.create(
            name="Math"
        )

        self.course = Course.objects.create(
            title="Math Course",
            description="abcd",
            organization=self.org,
            type=self.course_type,
            instructor=self.instructor_membership,
            is_active=True,
            status=Course.Status.PUBLISHED
        )

        self.second_course = Course.objects.create(
            title="Second Course",
            description="Should not appear",
            organization=self.second_org,
            type=self.course_type,
            instructor=self.second_instructor_membership,
            is_active=True,
            status=Course.Status.PUBLISHED
        )

        self.draft_course = Course.objects.create(
            title="Draft Course",
            description="Draft",
            organization=self.org,
            type=self.course_type,
            instructor=self.instructor_membership,
            is_active=True,
            status=Course.Status.DRAFT
        )

        self.second_draft_course = Course.objects.create(
            title="Second Draft",
            description="Another Course",
            organization=self.second_org,
            type=self.course_type,
            instructor=self.second_instructor_membership,
            is_active=True,
            status=Course.Status.DRAFT
        )

        self.lesson = Lesson.objects.create(
            title="Algebric Expressions",
            course=self.course,
            content="abcd",
            video_link="http://test.com/video/",
            order=1,
            status=Lesson.Status.PUBLISHED
        )


    def test_student_can_access_lessons_endpoint(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("course-lessons", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Algebric Expressions")
        # 


# # ----------------------- COURSE CREATION TEST CASES -----------------------

    def test_owner_can_create_course(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = "/api/v1/course/"

        data = {
            "title": "Owner Course",
            "description": "Created by owner",
            "instructor_id": self.instructor_membership.id,
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)

        self.assertIn("id", response.data)

        course = Course.objects.get(id=response.data["id"])

        self.assertEqual(course.title, "Owner Course")
        self.assertEqual(course.description, "Created by owner")
        self.assertEqual(course.instructor, self.instructor_membership)


    def test_admin_cannot_create_course(self):
        self.authenticate(
            self.admin_user,
            self.admin_membership
        )

        url = "api/v1/course/"

        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Course.objects.filter(title="Physics").exists())
        self.assertFalse(Course.objects.filter(description="Basic Physics").exists())


    def test_instructor_can_create_course(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = "/api/v1/course/"
        
        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        course_id = response.data["id"]
        course = Course.objects.get(id=course_id)

        self.assertIn("id", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Physics")
        self.assertEqual(response.data["description"], "Basic Physics")
        self.assertEqual(response.data["type"], self.course_type.id)
        self.assertEqual(response.data["is_active"], True)
        self.assertEqual(course.title, "Physics")
        self.assertEqual(course.instructor, self.instructor_membership)


    def test_student_cannot_create_course(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = "api/v1/course/"

        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(Course.objects.filter(title="Physics").exists())
        self.assertFalse(Course.objects.filter(description="Basic Physics").exists())

    def test_unauthorized_user_cannot_create_course(self):
        url = "/api/v1/course/"

        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 401)

    def test_course_creation_fails_without_required_field(self):
        token = get_token(
            self.owner_user,
            self.owner_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = "/api/v1/course/"

        data = {
            "description": "Basic Physics",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)


    def test_instructor_cannot_assign_another_instructor_for_course_creation(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = "/api/v1/course/"

        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "instructor_id": self.second_instructor_membership.id,
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Course.objects.filter(title="Physics").exists())

    def test_course_creation_failed_with_invalid_type(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = "/api/v1/course/"

        data = {
            "title": "Physics",
            "description": "Basic Physics",
            "type": 9999,
            "is_active": True
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Course.objects.filter(title="Physics").exists())

# # ----------------------- COURSE LIST TEST CASES -----------------------

    def test_owner_can_list_courses(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = "/api/v1/course/"

        response = self.client.get(url)

        # response.data = [
        #     {
        #         'id': 3,
        #         'organization': 1,
        #         'title': 'Draft Course',
        #         'description': 'Draft',
        #         'type': 1,
        #         'is_active': True,
        #         'status': 'DRAFT',
        #         'published_at': None
        #     },
        #     {
        #         'id': 1,
        #         'organization': 1,
        #         'title': 'Math Course',
        #         'description': 'abcd',
        #         'type': 1,
        #         'is_active': True,
        #         'status': 'PUBLISHED',
        #         'published_at': None
        #     }
        # ]

        course_data = next((item for item in response.data if item["id"] == self.course.id), None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], "Math Course")
        self.assertEqual(course_data["type"], self.course_type.id)
        self.assertEqual(course_data["status"], Course.Status.PUBLISHED)

        course = Course.objects.get(id=self.course.id)

        self.assertEqual(course.title, "Math Course")
        self.assertEqual(course.organization, self.org)
        self.assertEqual(course.instructor, self.instructor_membership)

    def test_instructor_can_list_courses(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = "/api/v1/course/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = next((item for item in response.data if item["id"] == self.course.id), None)

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], "Math Course")
        self.assertEqual(course_data["type"], self.course_type.id)
        self.assertEqual(course_data["status"], Course.Status.PUBLISHED)

        course = Course.objects.get(id=self.course.id)

        self.assertEqual(course.title, "Math Course")
        self.assertEqual(course.organization, self.org)
        self.assertEqual(course.instructor, self.instructor_membership)

        # make sure no course is in the response that belongs to some other instructor

    def test_admin_can_list_courses(self):
        self.authenticate(
            self.admin_user,
            self.admin_membership
        )

        url = "/api/v1/course/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = next((item for item in response.data if item["id"] == self.course.id), None)

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], self.course.title)
        self.assertEqual(course_data["type"], self.course_type.id)


    def test_student_can_list_courses(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("course-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = response.data[0]

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], self.course.title)
        self.assertEqual(course_data["type"], self.course.type.id)

    def test_unauthenticated_user_cannot_list_courses(self):
        url = "/api/v1/course/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_user_only_sees_courses_of_current_organization(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("course-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        course_data = response.data[0]


        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], self.course.title)
        self.assertEqual(course_data["type"], self.course.type.id)

        self.assertNotEqual(course_data["id"], self.second_course.id)
        self.assertNotEqual(course_data["title"], self.second_course.title)

# # ----------------------- COURSE RETRIEVE TEST CASES -----------------------

    def test_owner_can_retrieve_course(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.data["title"], self.course.title)
        self.assertEqual(response.data["description"], self.course.description)
        self.assertEqual(response.data["type"], self.course.type.id)

    def test_admin_can_retrieve_course(self):
        self.authenticate(
            self.admin_user,
            self.admin_membership
        )

        url = reverse("course-detail", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.data["title"], self.course.title)
        self.assertEqual(response.data["description"], self.course.description)
        self.assertEqual(response.data["type"], self.course.type.id)

    def test_instructor_can_retrieve_course(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )
        
        url = reverse("course-detail", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.data["title"], self.course.title)
        self.assertEqual(response.data["description"], self.course.description)
        self.assertEqual(response.data["type"], self.course.type.id)

    def test_student_can_retrieve_course(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("course-detail", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.data["title"], self.course.title)
        self.assertEqual(response.data["description"], self.course.description)
        self.assertEqual(response.data["type"], self.course.type.id)

    def test_unauthorized_user_cannot_retrieve_course(self):
        url = reverse("course-detail", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_user_cannot_retrieve_course_from_another_organization(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("course-detail", args=[self.second_course.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_non_existing_course_returns_404(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[9999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


# ----------------------- COURSE UPDATE TEST CASES -----------------------

    def test_published_course_cannot_be_updated(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[self.course.id])

        data = {
            "title": "Updated Title"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 400)

        self.assertIn("You cannot update an already published course", str(response.data))

        self.course.refresh_from_db()

        self.assertEqual(self.course.title, "Math Course")

    def test_owner_can_update_draft_courses(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "title": "Updated Course",
            "description": "Updated Description",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.put(url, data)

        self.draft_course.refresh_from_db()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.draft_course.title, "Updated Course")
        self.assertEqual(self.draft_course.description, "Updated Description")
        self.assertEqual(self.draft_course.is_active, True)
        self.assertEqual(self.draft_course.status, Course.Status.DRAFT)

    def test_admin_cannot_update_draft_course(self):
        self.authenticate(
            self.admin_user,
            self.admin_membership
        )

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "title": "Admin Updated",
            "description": "Updated by admin",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.put(url, data)

        self.draft_course.refresh_from_db()

        self.assertEqual(response.status_code, 403)

    def test_instructor_can_update_own_draft_course(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "title": "Instructor Updated",
            "description": "Updated by instructor",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.put(url, data)

        self.draft_course.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.draft_course.title, "Instructor Updated")
        self.assertEqual(self.draft_course.description, "Updated by instructor")

    def test_student_cannot_update_course(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "title": "Updated Title"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_cannot_update_course(self):

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "title": "Updated Title"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 401)

    def test_instructor_cannot_update_another_instructor_course(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("course-detail", args=[self.second_draft_course.id])

        data = {
            "title": "Illegal Update"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_update_course_from_another_organization(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[self.second_draft_course.id])

        data = {
            "title": "Illegal Update"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 404)

    def test_course_update_fails_with_invalid_data(self):
        self.authenticate(
            self.owner_user,
            self.owner_membership
        )

        url = reverse("course-detail", args=[self.draft_course.id])

        data = {
            "description": "Updated Description",
            "type": self.course_type.id,
            "is_active": True
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)