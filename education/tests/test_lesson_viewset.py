from django.urls import reverse
from rest_framework import status
from education.tests.test_course_viewset import get_token
from rest_framework.test import APITestCase
from organization.models import Membership, Organization
from education.models import Lesson, Course, CourseType, Enrollment, Feedback
from django.contrib.auth import get_user_model

User = get_user_model()


class LessonUpdateViewSetTests(APITestCase):

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

        self.second_student_user = User.objects.create_user(
            username="second student",
            password="testuser@123"
        )

        self.new_student_user = User.objects.create_user(
            username="new student",
            password="testuser@123"
        )

        self.non_enrolled_student_user = User.objects.create_user(
            username="non_enrolled_student",
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

        self.second_student_membership = Membership.objects.create(
            user=self.second_student_user,
            organization=self.org,
            role=Membership.Role.STUDENT,
            is_active=True
        )

        self.new_student_membership = Membership.objects.create(
            user=self.new_student_user,
            organization=self.org,
            role=Membership.Role.STUDENT,
            is_active=True
        )

        self.non_enrolled_student_membership = Membership.objects.create(
            user=self.non_enrolled_student_user,
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

        self.empty_course = Course.objects.create(
            title="Empty Course",
            description="No lessons",
            organization=self.org,
            type=self.course_type,
            instructor=self.instructor_membership,
            is_active=True,
            status=Course.Status.DRAFT
        )

        self.no_enrollment_course = Course.objects.create(
            title="No enrollment course",
            description="No enrollments",
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

        self.draft_course_lesson = Lesson.objects.create(
            title="Draft course lesson 1",
            course=self.draft_course,
            content="abcdefghijklmnpqrstuvwxyz",
            video_link="http://test.com/video/",
            order=1,
            status=Lesson.Status.DRAFT
        )

        self.second_draft_course_lesson = Lesson.objects.create(
            title="Second draft course lesson 1",
            course=self.second_draft_course,
            content="abcdefghijklmnpqrstuvwxyz",
            video_link="http://test.com/video/",
            order=1,
            status=Lesson.Status.DRAFT
        )

        self.lesson_other_org = Lesson.objects.create(
            title="Other Org Lesson",
            course=self.second_course,
            content="Other org content",
            video_link="http://test.com/video/",
            order=1,
            status=Lesson.Status.PUBLISHED
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student_membership,
            organization=self.org,
            course=self.course
        )

        self.new_student_enrollment = Enrollment.objects.create(
            student=self.new_student_membership,
            organization=self.org,
            course=self.course
        )

        self.approved_feedback = Feedback.objects.create(
            organization=self.org,
            student=self.student_membership,
            course=self.course,
            rating=5,
            comment="Excellent course",
            is_approved=True
        )

        self.pending_feedback = Feedback.objects.create(
            organization=self.org,
            student=self.second_student_membership,
            course=self.course,
            rating=1,
            comment="Pending",
            is_approved=False
        )


    def test_update_lesson_success(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Updated Title",
            "content": "Updated Content",
            "video_link": "https://example.com/new"
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Title")

    def test_partial_update_success(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Partially Updated"
        }

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Partially Updated")

    def test_update_denied_for_student(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Hack Attempt"
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_denied_for_student(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Hack Attempt"
        }

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_validation_fails_empty_content_and_video(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "content": "",
            "video_link": ""
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_video_url(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "video_link": "invalid-url"
        }

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lesson_other_org_not_accessible(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson_other_org.id])

        payload = {
            "title": "Should Not Work"
        }

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_lesson_unauthenticated_user(self):
        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Unauthorized Update Attempt"
        }

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_lesson_success_by_instructor(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_delete_lesson_forbidden_for_student(self):
        self.authenticate(
            self.student_user,
            self.student_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_unauthenticated(self):
        url = reverse("lesson-detail", args=[self.lesson.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_non_existent_lesson_returns_404(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[99999])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_lesson_other_org_forbidden(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson_other_org.id])

        payload = {
            "title": "Hacked Update"
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_other_org_forbidden(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson_other_org.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_put_invalid_video_url_rejected(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Test",
            "content": "Test content",
            "video_link": "not-a-valid-url"
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_empty_title_fails(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "",
            "content": "Valid content",
            "video_link": "https://example.com/video"
        }

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_overwrites_all_fields(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Fully Updated Title",
            "content": "Fully Updated Content",
            "video_link": "https://example.com/full-update"
        }

        self.client.put(url, payload)

        self.lesson.refresh_from_db()

        self.assertEqual(self.lesson.title, "Fully Updated Title")
        self.assertEqual(self.lesson.content, "Fully Updated Content")
        self.assertEqual(self.lesson.video_link, "https://example.com/full-update")
    
    def test_patch_does_not_overwrite_other_fields(self):
        self.authenticate(
            self.instructor_user,
            self.instructor_membership
        )

        original_content = self.lesson.content
        original_video = self.lesson.video_link

        url = reverse("lesson-detail", args=[self.lesson.id])

        payload = {
            "title": "Only Title Changed"
        }

        self.client.patch(url, payload)

        self.lesson.refresh_from_db()

        self.assertEqual(self.lesson.title, "Only Title Changed")
        self.assertEqual(self.lesson.content, original_content)
        self.assertEqual(self.lesson.video_link, original_video)