import uuid
from django.db import models
from core.models import TimeStampModel
from django.conf import settings


class Organization(TimeStampModel):
    """
    Represents an Organization (e.g., School, College, University, Academy) on which the whole system depends
    """

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizations")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    total_admins = models.PositiveIntegerField(default=0)
    total_instructors = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class OrganizationSetting(TimeStampModel):
    """
    Keeps all the configurations of the Organization
    """

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="settings")
    max_admins = models.PositiveIntegerField(default=10)
    max_instructors = models.PositiveIntegerField(default=50)
    max_students = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return f"Settings ( {self.organization.name} )"

class Membership(TimeStampModel):
    """
    Tracks the membership of each user in organization
    Each user like Owner, Admin, Instructor and Student is a member of the organization
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        STUDENT = "STUDENT", "Student"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "organization"],
                name = "unique_user_per_organization"
            )
        ]


    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_staff(self):
        return self.role in [
            self.Role.OWNER,
            self.Role.ADMIN,
            self.Role.INSTRUCTOR
        ]
    
    def owns_course(self, course):
        return course.instructor_id == self.id


    def can_view_course(self, course):
        """
        User and course must belong to the same organization,
        Staff can view all courses,
        Students can only view courses that are published and active,
        Everyone else cannot view the course
        """

        if course.organization_id != self.organization_id:
            return False

        if self.is_staff:
            return True

        if self.is_student:
            return course.is_published and course.is_active

        return False

    def can_create_course(self):
        """
        Only owners and instructors are allowed to create courses
        """

        return self.role in [
            self.Role.OWNER,
            self.Role.INSTRUCTOR
        ]


    def can_edit_course(self, course):
        """
        Must belong to the same organization.
        Owners can edit any course
        Instructors can only edit their own courses.
        Others cannot edit
        """

        if course.organization_id != self.organization_id:
            return False

        if self.is_owner:
            return True

        if self.is_instructor:
            return course.instructor_id == self.id

        return False


    def can_delete_course(self, course):
        """
        If user can edit a course, he can delete it too
        """
        return self.can_edit_course(course)


    def can_publish_course(self, course):
        """
        If user can edit a course, he can publish it too
        """
        return self.can_edit_course(course)


    def is_enrolled_in(self, course):
        return course.enrollments.filter(student_id=self.id).exists()


    def can_view_lesson(self, lesson):
        """
        Must be in the same organization
        Owners/Admins can view everything
        Instructors can view lessons in their own courses
        Students can only view published lessons of courses they're actively enrolled in
        """

        course = lesson.course

        if course.organization_id != self.organization_id:
            return False
        
        if self.is_owner or self.is_admin:
            return True

        if self.is_instructor:
            return course.instructor_id == self.id
        if self.is_student:
            return (
                course.is_published and
                course.is_active and 
                self.is_enrolled_in(course)
            )

        return False


    def can_edit_lesson(self, lesson):
        """
        If user can edit the course, he can also edit its lessons
        """
        return self.can_edit_course(lesson.course)


    def can_delete_lesson(self, lesson):
        """
        If user can edit lessons, he can delete lessons
        """
        return self.can_edit_lesson(lesson)


    def can_enroll_in(self, course):
        """
        Only students can enroll, and only in courses that are published, active, and in their organization
        """

        if not self.is_student:
            return False

        if course.organization_id != self.organization_id:
            return False

        return (
            course.is_active and
            course.status == course.Status.PUBLISHED
        )


    def can_view_enrollments_for(self, course):
        """
        Must belong to the same organization.
        Owners/Admins can see all enrollments.
        Instructors can only see enrollments for their own courses.
        Others cannot view enrollments
        """

        if course.organization_id != self.organization_id:
            return False

        if self.is_owner or self.is_admin:
            return True
        
        if self.is_instructor:
            return course.instructor_id == self.id
        
        return False

    def can_create_lesson(self, course):
        return self.can_edit_course(course)
    
    def can_view_lessons(self, course):
        if course.organization_id != self.organization_id:
            return False

        if self.is_owner or self.is_admin:
            return True

        if self.is_instructor:
            return course.instructor_id == self.id

        if self.is_student:
            return course.is_published and course.is_active

        return False

    def can_cancel_enrollment(self, course):
        return self.is_student

    def can_view_course_feedbacks(self, course):
        return self.can_view_course(course)

    def can_view_enrollment_status(self, course):
        return self.can_view_course(course)

    def can_view_my_enrollments(self):
        return self.is_student

    def __str__(self):
        return f"{self.user.username} ( {self.role} ) - {self.organization.name}"


class OrganizationJoinLink(TimeStampModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISABLED = "DISABLED", "Disabled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="join_links")
    created_by = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="created_join_links")
    role = models.CharField(max_length=10, choices=Membership.Role.choices)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    max_users = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_expired = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_valid(self):
        return self.status == self.Status.ACTIVE and self.is_expired == False

    def __str__(self):
        return f"{self.organization} - {self.role}"