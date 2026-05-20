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

        self.lesson = Lesson.objects.create(
            title="Algebric Expressions",
            course=self.course,
            content="abcd",
            video_link="http://test.com/video/",
            order=1,
            status=Lesson.Status.PUBLISHED
        )


    def test_student_can_access_lessons_endpoint(self):
        token = get_token(
            self.student_user,
            self.student_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


        url = reverse("course-lessons", args=[self.course.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Algebric Expressions")


# ----------------------- COURSE CREATION TEST CASES -----------------------

    def test_owner_can_create_course(self):
        token = get_token(
            self.owner_user,
            self.owner_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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
        token = get_token(
            self.admin_user,
            self.admin_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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
        token = get_token(
            self.instructor_user,
            self.instructor_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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
        token = get_token(
            self.student_user,
            self.student_membership
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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


# ----------------------- COURSE LIST TEST CASES -----------------------

    def test_owner_can_list_courses(self):
        token = get_token(
            self.owner_user,
            self.owner_membership
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = "/api/v1/course/"

        response = self.client.get(url)
        course_data = response.data[0]

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
        token = get_token(
            self.instructor_user,
            self.instructor_membership
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = "/api/v1/course/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = response.data[0]

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], "Math Course")
        self.assertEqual(course_data["type"], self.course_type.id)
        self.assertEqual(course_data["status"], Course.Status.PUBLISHED)

        course = Course.objects.get(id=self.course.id)

        self.assertEqual(course.title, "Math Course")
        self.assertEqual(course.organization, self.org)
        self.assertEqual(course.instructor, self.instructor_membership)


    def test_admin_can_list_courses(self):
        token = get_token(
            self.admin_user,
            self.admin_membership
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = "/api/v1/course/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = response.data[0]

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], self.course.title)
        self.assertEqual(course_data["type"], self.course_type.id)


    def test_student_can_list_courses(self):
        token = get_token(
            self.student_user,
            self.student_membership
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("course-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        course_data = response.data[0]

        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["title"], self.course.title)
        self.assertEqual(course_data["type"], self.course.type.id)