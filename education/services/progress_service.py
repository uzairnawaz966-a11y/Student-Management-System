from education.models import LessonProgress, Progress
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from education.models import Lesson
from organization.models import OrganizationJoinLink, Membership

class ProgressService:

    @staticmethod
    def recalculate_progress(enrollment):
        """
        Recalculates and updates progress for an enrollment
        Returns Progress object
        Progress formula: Completed Lessons / Total Lessons × 100
        """

        total_lessons = enrollment.course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()

        if total_lessons == 0:
            percentage = 0
        else:
            percentage = (completed_lessons/total_lessons) * 100

        progress, _ = Progress.objects.get_or_create(enrollment=enrollment)

        progress.percentage = int(percentage)
        progress.is_completed = (percentage == 100)

        if progress.is_completed:
            progress.completed_at = timezone.now()
        else:
            progress.completed_at = None

        progress.save()

        return progress

    @staticmethod
    def mark_lesson_completed(enrollment, lesson):
        """
        Marks a lesson as completed and updates progress
        Returns updated Progress object
        """

        if lesson.status == Lesson.Status.DRAFT:
            raise PermissionDenied(
                "Draft lessons cannot be completed"
            )

        lesson_progress, created = LessonProgress.objects.update_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        if not lesson_progress.is_completed:
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save(
                update_fields=["is_completed", "completed_at"]
            )

        return ProgressService.recalculate_progress(enrollment)

    @staticmethod
    def join_organization(user, token):
        try:
            link = OrganizationJoinLink.objects.get(
                token=token,
                status=OrganizationJoinLink.Status.ACTIVE
            )
        except OrganizationJoinLink.DoesNotExist:
            raise ValueError("Invalid or expired link")
        if link.max_users and link.used_count >= link.max_users:
            link.status = OrganizationJoinLink.Status.DISABLED
            link.save(update_fields=["status"])
            raise ValueError("Join limit reached")
    
        if Membership.objects.filter(user=user, organization=link.organization).exists():
            raise ValueError("Already a member")
            