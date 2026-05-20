from rest_framework.permissions import BasePermission




ROLE_ACTIONS = {
    "OWNER": {
        "CourseViewSet": [
            "list", "retrieve", "create", "update", "partial_update",
            "destroy", "publish", "create_lesson", "lessons", "course_enrollments",
            "feedbacks"
        ],
        "LessonViewSet": [
            "list", "retrieve", "create", "update", "partial_update", "destroy"
        ]
    },

    "INSTRUCTOR": {
        "CourseViewSet": [
            "list", "retrieve", "create", "update", "partial_update",
            "destroy", "publish", "create_lesson", "lessons", "course_enrollments",
            "feedbacks"
        ],
        "LessonViewSet": [
            "list", "retrieve", "create", "update", "partial_update",
            "destroy"
        ]
    },

    "ADMIN": {
        "CourseViewSet": ["list", "retrieve", "lessons", "feedbacks"],
        "LessonViewSet": ["list", "retrieve"]
    },

    "STUDENT": {
        "CourseViewSet": [
            "list", "retrieve", "enroll", "cancel_enrollment", "lessons", "my_enrollments",
            "complete_lesson", "feedback", "enrollment_status", "feedbacks"
        ],
        "LessonViewSet": ["list", "retrieve"]
    }
}



class CoursePermission(BasePermission):
    def has_permission(self, request, view):
        membership = request.membership

        role_rules = ROLE_ACTIONS.get(membership.role, {})

        allowed_actions = role_rules.get(view.__class__.__name__, [])

        return view.action in allowed_actions


    def has_object_permission(self, request, view, obj):
        membership = request.membership

        if view.__class__.__name__ == "CourseViewSet":
            return membership.can_view_course(obj)

        if view.__class__.__name__ == "LessonViewSet":
            return membership.can_view_course(obj.course)

        return False





























# COURSE_ACTIONS_FOR_ROLE = {
#     Membership.Role.OWNER: [
#             'list', 'retrieve', 'create',
#             'update', 'partial_update', 'destroy',
#             'publish', 'lessons', 'lesson',
#             'create_lesson', 'enrollments', 'update_lesson',
#             'partial_update_lesson', 'delete_lesson'
#     ],

#     Membership.Role.ADMIN: [
#             'list', 'retrieve', 'lessons',
#             'lesson', 'enrollments'
#     ],

#     Membership.Role.INSTRUCTOR: [
#             'list', 'retrieve', 'create',
#             'update', 'partial_update', 'publish',
#             'destroy', 'lessons', 'lesson',
#             'create_lesson', 'update_lesson', 'partial_update_lesson',
#             'delete_lesson', 'enrollments'
#     ],

#     Membership.Role.STUDENT: [
#             'list', 'retrieve', 'lessons',
#             'lesson', 'enroll', 'enrollments',
#     ]
# }

# OBJECT_LEVEL_COURSE_ACTION_MAPPING = [
#     ("retrieve", "can_view_course"),
#     ("update", "can_edit_course"),
#     ("partial_update", "can_edit_course"),
#     ("destroy", "can_delete_course"),
#     ("publish", "can_publish_course"),
#     ("enroll", "can_enroll_in"),
#     ("enrollments", "can_view_enrollments_for")
# ]

# OBJECT_LEVEL_LESSON_ACTION_MAPPING = [
#     ("lesson", "can_view_lesson"),
#     ("update_lesson", "can_edit_lesson"),
#     ("partial_update_lesson", "can_edit_lesson"),
#     ("delete_lesson", "can_edit_lesson")
# ]


# def get_method_from_mapping(action, mapping):
#     for act, method in mapping:
#         if act == action:
#             return method
#     return None










    # def has_object_permission(self, request, view, obj):
    #     membership = request.membership

    #     method_name = get_method_from_mapping(view.action, OBJECT_LEVEL_LESSON_ACTION_MAPPING)
    #     if method_name:
    #         method = getattr(membership, method_name)
    #         lesson = view.get_lesson()
    #         return method(lesson)

    #     method_name = get_method_from_mapping(view.action, OBJECT_LEVEL_COURSE_ACTION_MAPPING)
    #     if method_name:
    #         method = getattr(membership, method_name)
    #         return method(obj)
        
    #     return False
 





























    # def has_object_permission(self, request, view, obj):
    #     membership = request.membership
        
    #     if obj.organization != membership.organization:
    #         return False

    #     if role == Membership.Role.OWNER:
    #         return True

    #     if role == Membership.Role.ADMIN:
    #         return view.action in  ["list", "retrieve"]

    #     if role == Membership.Role.INSTRUCTOR:
    #         return obj.instructor == membership

    #     return False








# class LessonPermission(BasePermission):

#     def has_permission(self, request, view):
#         membership = request.membership
#         role = membership.role

#         if view.action in ["list", "retrieve"]:
#             return role in [
#                 Membership.Role.OWNER,
#                 Membership.Role.ADMIN,
#                 Membership.Role.INSTRUCTOR,
#                 Membership.Role.STUDENT
#             ]
        
#         if view.action in ["create", "update", "partial_update", "destroy"]:
#             return role in [
#                 Membership.Role.OWNER,
#                 Membership.Role.INSTRUCTOR
#             ]

#         return False


#     def has_object_permission(self, request, view, obj):
#         membership = request.membership
#         role = membership.role

#         if obj.course.organization != membership.organization:
#             return False

#         if role == Membership.Role.OWNER:
#             return True
        
#         if role == Membership.Role.ADMIN:
#             return view.action in ["list", "retrieve"]
        
#         if role == Membership.Role.INSTRUCTOR:
#             return obj.course.instructor == membership
        
#         return False


# class EnrollmentPermission(BasePermission):
#     def has_permission(self, request, view):
#         role = request.membership.role

#         if view.action == 'create':
#             return role == Membership.Role.STUDENT
        
#         if view.action == 'list':
#             return role in [
#                 Membership.Role.STUDENT,
#                 Membership.Role.INSTRUCTOR
#             ]
        
#         return False






















        # if view.action in ["list", "retrieve"]:
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.ADMIN,
        #         Membership.Role.INSTRUCTOR,
        #         Membership.Role.STUDENT
        #     ]

        # if view.action == "create":
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.INSTRUCTOR
        #     ]

        # if view.action in ["update", "partial_update", "publish", "destroy"]:
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.INSTRUCTOR
        #     ]

        # if view.action in ['lessons', 'lesson']:
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.ADMIN,
        #         Membership.Role.INSTRUCTOR,
        #         Membership.Role.STUDENT
        #     ]

        # if view.action == 'create_lesson':
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.INSTRUCTOR
        #     ]

        # if view.action == 'enroll':
        #     return role == Membership.Role.STUDENT
        
        # if view.action == 'enrollments':
        #     return role in [
        #         Membership.Role.INSTRUCTOR,
        #         Membership.Role.STUDENT
        #     ]

        # if view.action in ["update_lesson", "partial_update_lesson", "delete_lesson"]:
        #     return role in [
        #         Membership.Role.OWNER,
        #         Membership.Role.INSTRUCTOR
        #     ]