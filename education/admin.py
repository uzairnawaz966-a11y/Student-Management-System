from django.contrib import admin
from education.models import (
    CourseType,
    Course,
    Lesson,
    Enrollment,
    Progress,
    LessonProgress,
    Feedback,
)

@admin.register(CourseType)
class CourseTypeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name"
    ]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "slug",
        "organization",
        "title",
        "description",
        "type",
        "instructor",
        "status",
        "is_active",
        "published_at",
        "status_changed_at",
        "scheduled_for",
        "failure_cause",
        "created_at",
        "updated_at",
    ]

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "course",
        "order",
        "status",
        "published_at",
        "status_changed_at",
        "scheduled_for",
        "failure_cause",
        "created_at",
        "updated_at",
    ]

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "organization",
        "student",
        "course",
        "enrolled_at",
        "is_cancelled",
        "cancel_reason",
        "canceled_at",
    ]


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "enrollment",
        "percentage",
        "is_completed",
        "completed_at",
    ]

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "enrollment",
        "lesson",
        "is_completed",
        "completed_at"
    ]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "organization",
        "course",
        "student",
        "rating",
        "comment",
        "created_at",
        "updated_at",
    ]