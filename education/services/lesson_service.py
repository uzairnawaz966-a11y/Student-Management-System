from rest_framework.exceptions import PermissionDenied
from education.models import Lesson


class LessonService:

    @staticmethod
    def get_lessons_for_course(membership, course):

        if course.organization_id != membership.organization_id:
            raise PermissionDenied("Invalid access")

        if membership.is_staff:

            if membership.is_instructor:
                if not membership.owns_course(course):
                    raise PermissionDenied("Not your course")

            return Lesson.objects.filter(course=course)

        if membership.is_student:
            return Lesson.objects.filter(
                course=course,
                status=Lesson.Status.PUBLISHED
            )


        return Lesson.objects.none()