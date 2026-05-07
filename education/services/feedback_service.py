from education.models import Enrollment, Feedback
from rest_framework.exceptions import PermissionDenied
from django.db import transaction


class FeedbackService:

    @staticmethod
    def get_valid_enrollment(student, course):
        enrollment = Enrollment.objects.filter(
            student=student,
            course=course,
            is_cancelled=False
        ).first()

        if not enrollment:
            raise PermissionDenied("You are not enrolled in this course")

        return enrollment


    @staticmethod
    @transaction.atomic
    def submit_feedback(student, course, organization, rating, comment):
        FeedbackService.get_valid_enrollment(student, course)

        feedback, created = Feedback.objects.update_or_create(
            student=student,
            course=course,
            defaults={
                "organization": organization,
                "rating": rating,
                "comment": comment
            }
        )

        return feedback, created