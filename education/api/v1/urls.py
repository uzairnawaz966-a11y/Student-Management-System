from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework_nested.routers import NestedDefaultRouter
from education.api.v1.views import (
    CourseViewSet,
    LessonViewSet
)


router = DefaultRouter()

router.register(r'course', CourseViewSet, basename="course")
router.register(r'lesson', LessonViewSet, basename="lesson")

# course_router = NestedDefaultRouter(router, r'course', lookup='course')

# course_router.register(r'lessons', LessonViewSet, basename="course-lessons")

urlpatterns = [
    path('', include(router.urls)),
    # path('', include(course_router.urls))
]





# 'course/course_id/lessons' -> add / list
# 'lessons/lesson_id' -> get / delete / update
# 'lessons/lesson_id/publish' -> get / delete / update
# router.register(r'lesson', LessonViewSet, basename="lesson")
