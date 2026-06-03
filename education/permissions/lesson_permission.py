from rest_framework.permissions import BasePermission


class LessonPermission(BasePermission):

    OBJECT_ACTION_MAP = {
        "retrieve": "can_view_lesson",
        "update": "can_edit_lesson",
        "partial_update": "can_edit_lesson",
        "destroy": "can_delete_lesson",
    }

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        membership = request.membership

        method_name = self.OBJECT_ACTION_MAP.get(view.action)

        if not method_name:
            return True

        checker = getattr(membership, method_name, None)

        if not checker:
            return False

        return checker(obj)