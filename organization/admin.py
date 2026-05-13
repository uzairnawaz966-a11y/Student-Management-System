from django.contrib import admin
from organization.models import (
    Organization,
    OrganizationSetting,
    Membership,
    OrganizationJoinLink,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "owner",
        "description",
        "is_active",
        "total_admins",
        "total_instructors",
        "total_students",
        "created_at",
        "updated_at",
    ]


@admin.register(OrganizationSetting)
class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "organization",
        "max_admins",
        "max_instructors",
        "max_students",
        "created_at",
        "updated_at",
    ]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "organization",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    ]


@admin.register(OrganizationJoinLink)
class OrganizationJoinLinkAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "organization",
        "created_by",
        "role",
        "token",
        "status",
        "max_users",
        "used_count",
        "created_at",
        "updated_at"
    ]