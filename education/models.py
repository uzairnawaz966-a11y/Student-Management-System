from core.models import TimeStampModel, PublishableModel
from organization.models import Membership
from organization.models import Organization
from django.utils import timezone
from django.utils.text import slugify
from django.db import models



def generate_unique_slug(model, base_slug, **filters):
    slug = base_slug
    counter = 1

    while model.objects.filter(slug=slug, **filters).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class CourseType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CourseManager(models.Manager):
    """
    Course Manager which fetches all the active courses within the given organization
    It returns the data according to the user role
    """

    def active(self):
        return self.filter(is_active=True)

    def get_active_courses(self, membership):

        queryset = self.active().filter(
            organization=membership.organization_id
        )

        if membership.is_owner or membership.is_admin:
            return queryset
        elif membership.is_instructor:
            return queryset.filter(instructor=membership)
        elif membership.is_student:
            return queryset.filter(status=Course.Status.PUBLISHED)
        return self.none()


class Course(TimeStampModel, PublishableModel):
    """
    Represents the course published by an instructor
    Also keeps the instructor of the courses
    """

    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    instructor = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="courses")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="courses")
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["organization", "instructor", "slug", "type"]

    objects = CourseManager()

    def publish_lessons(self):
        self.lessons.update(
            status=self.Status.PUBLISHED,
            published_at=timezone.now(),
            status_changed_at=timezone.now(),
            failure_cause=None
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)

            self.slug = generate_unique_slug(
                Course,
                base_slug,
                organization=self.organization,
                instructor=self.instructor,
                type=self.type
            )
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.title} by {self.instructor.user}"


class Lesson(TimeStampModel, PublishableModel):
    """
    Represents Lessons of different courses
    Also keeps an eye on the course
    """

    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    video_link = models.URLField(max_length=300, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveIntegerField()
    slug = models.SlugField()

    class Meta:
        ordering = ["order"]
        unique_together = ["course", "order"]


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)

            self.slug = generate_unique_slug(
                Lesson,
                base_slug,
                course=self.course
            )

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """
    Tracks all the courses which are enrolled by students
    """

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.TextField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course', 'organization'],
                name='unique_enrollment'
            )
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} enrolled in {self.course.title}"


class Progress(models.Model):
    """
    Tracks progress of students who are enrolled in any course
    """

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="progress")
    percentage = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Progresses"

    def __str__(self):
        return f"{self.enrollment.student.user.get_full_name()} - {self.percentage}%"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lesson_progress")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "lesson Progresses"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"],
                name="lesson_progress_uniqueness"
            )
        ]


class Feedback(TimeStampModel):
    """
    Course ratings and reviews by enrolled students
    """

    class Rating(models.IntegerChoices):
        ZERO = 0, 'Zero'
        ONE = 1, 'One'
        TWO = 2, 'Two'
        THREE = 3, 'Three'
        FOUR = 4, 'Four'
        FIVE = 5, 'Five'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedback")
    student = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="feedback")
    rating = models.PositiveSmallIntegerField(choices=Rating.choices)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"],
                name="unique_course_feedback"
            )
        ]

        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["course", "rating"])
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.title}"