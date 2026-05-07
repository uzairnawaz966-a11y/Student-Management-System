from education.models import LessonProgress, Progress
from django.utils import timezone

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

        lesson_progress, created = LessonProgress.objects.update_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        if not lesson_progress.is_completed:
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save(update_fields=["is_completed", "completed_at"])


        return ProgressService.recalculate_progress(enrollment)