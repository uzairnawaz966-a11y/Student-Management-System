from django.contrib import admin
from user_auth.models import (
    Owner,
    Admin,
    Instructor,
    Student,
    AccountActivationToken,
)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "membership",
        "full_name",
        "age",
        "city",
        "contact_number",
        "cnic",
        "profile_picture",
        "joined_at",
    ]


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "membership",
        "full_name",
        "age",
        "city",
        "contact_number",
        "cnic",
        "subjects",
        "managed_classes",
        "current_salary",
        "qualification",
        "experience",
        "profile_picture",
        "joined_at",
    ]


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "membership",
        "full_name",
        "age",
        "city",
        "contact_number",
        "cnic",
        "subjects",
        "assigned_classes",
        "current_salary",
        "qualification",
        "experience",
        "profile_picture",
        "joined_at",
    ]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "membership",
        "full_name",
        "age",
        "city",
        "contact_number",
        "cnic",
        "grade",
        "roll_number",
        "section",
        "profile_picture",
        "joined_at",
    ]


@admin.register(AccountActivationToken)
class AccountActivationTokenAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "token",
        "created_at",
        "expiration_date",
        "is_used",
        "is_expired",
    ]


# PostgreSQL database name = management_db
# User name = uzair
# password = pass@123