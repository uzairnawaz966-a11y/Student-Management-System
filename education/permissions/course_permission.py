from rest_framework.permissions import BasePermission


class CoursePermission(BasePermission):

    OBJECT_ACTION_MAP = {
        "retrieve": "can_view_course",
        "update": "can_edit_course",
        "partial_update": "can_edit_course",
        "destroy": "can_delete_course",
        "publish": "can_publish_course",
        "enroll": "can_enroll_in",
        "course_enrollments": "can_view_enrollments_for",
        "create_lesson": "can_create_lesson",
        "lessons": "can_view_course",
        "cancel_enrollment": "can_cancel_enrollment",
        "course_feedbacks": "can_view_course_feedbacks",
        "enrollment_status": "can_view_enrollment_status",
    }

    def has_permission(self, request, view):
        membership = request.membership

        if view.action == "create":
            return membership.can_create_course()

        if view.action == "my_enrollments":
            return membership.can_view_my_enrollments()

        return True

    def has_object_permission(self, request, view, obj):
        membership = request.membership

        permission_method = self.OBJECT_ACTION_MAP.get(view.action)

        if permission_method is None:
            return True

        return getattr(membership, permission_method)(obj)