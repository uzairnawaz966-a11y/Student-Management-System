from education.services.course_service import CourseService
from education.services.progress_service import ProgressService
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from education.permissions import CoursePermission
from education.api.v1.serializers import (
    CourseSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
    LessonSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer,
    LessonPartialUpdateSerializer,
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    FeedbackSerializer,
    FeedbackCreateSerializer,
)
from education.models import (
    Course,
    Lesson,
    Enrollment,
    Feedback
)


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CoursePermission]
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        
        if self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer

        return CourseSerializer

    def get_queryset(self):
        return Course.objects.get_active_courses(
            membership=self.request.membership
        )

    def perform_create(self, serializer):
        course = CourseService.create_course(
            membership=self.request.membership,
            validated_data=serializer.validated_data,
        )
        serializer.instance = course

    def perform_update(self, serializer):
        CourseService.update_course(
            membership=self.request.membership,
            course=self.get_object(),
            serializer=serializer
        )

    def perform_destroy(self, instance):
        CourseService.destroy_course(
            membership=self.request.membership,
            instance=instance
        )


    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        CourseService.publish_course(
            membership=self.request.membership,
            course=self.get_object()
        )
        return Response(
            {
                "message": "Course published successfully"
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path="create-lesson")
    def create_lesson(self, request, pk=None):
        course = self.get_object()
        membership = request.membership

        if membership.can_edit_course(course):

            serializer = LessonCreateSerializer(
                data=request.data,
                context = {
                    "request": request,
                    "course": course
                }
            )
            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied("You cannot create lessons for this course")

    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        course = self.get_object()
        membership = request.membership

        lessons = Lesson.objects.filter(course=course)

        if membership.is_student and not membership.is_enrolled_in(course):
            raise PermissionDenied("You are not enrolled in this course")

        if membership.is_instructor and not membership.owns_course(course):
            raise PermissionDenied("You can only access your own courses")

        serializer = LessonSerializer(lessons, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        course = self.get_object()
        membership = request.membership

        if membership.can_enroll_in(course):

            serializer = EnrollmentCreateSerializer(
                data={},
                context={
                    "request": request,
                    "view": self
                }
            )
            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(
                    {
                        "message": "You are enrolled successfully"
                    },
                status=status.HTTP_201_CREATED
            )
        else:
            raise PermissionDenied("You cannot enroll in unpublished or inactive courses")

    @action(detail=True, methods=["get"])
    def course_enrollments(self, request, pk=None):
        """
        This API is only for instructor
        Gives all the enrollments of those students who has enrolled in this specific course
        """

        course = self.get_object()
        membership = request.membership

        if membership.can_view_enrollments_for(course):
            queryset = Enrollment.objects.filter(course=course)

            serializer = EnrollmentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied("You are not allowed to access this api")

    @action(detail=True, methods=['post'])
    def cancel_enrollment(self, request, pk=None):
        course = self.get_object()
        membership = request.membership

        if not membership.is_student:
            raise PermissionDenied("You cannot perform this action")

        try:
            enrollment = Enrollment.objects.get(
                student=membership,
                course=course,
                organization=membership.organization
            )
        except Enrollment.DoesNotExist:
            raise ValidationError("You are not enrolled in this course")

        enrollment.delete()

        return Response(
            {
                "message": "Enrollment cancelled"
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        serializer = FeedbackCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "view": self
            }
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                "message": "Feedback posted",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"])
    def enrollment_status(self, request, pk=None):
        course = self.get_object()
        membership = request.membership

        is_enrolled = membership.is_enrolled_in(course)

        return Response(
            {
                "course_id": course.id,
                "is_enrolled": is_enrolled
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path="enrollments/me")
    def my_enrollments(self, request):
        membership = request.membership

        queryset = Enrollment.objects.filter(
            student=membership,
            organization=membership.organization
        ).order_by("-created_at")

        serializer = EnrollmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def feedbacks(self, request, pk=None):
        course = self.get_object()
        queryset = Feedback.objects.filter(
            course=course,
            is_approved=True
        ).order_by("-created_at")

        serializer = FeedbackSerializer(
            queryset,
            many=True,
            context={
                "request": request
            }
        )
        return Response(serializer.data)


class LessonViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return LessonPartialUpdateSerializer
        return LessonUpdateSerializer

    def get_queryset(self):
        membership = self.request.membership

        queryset = Lesson.objects.filter(
            course__organization_id=membership.organization_id
        )
        return queryset


    @action(detail=True, methods=['post'])
    def complete_lesson(self, request, pk=None):
        lesson = self.get_object()
        membership = request.membership

        try:
            enrollment = Enrollment.objects.get(
                student=membership,
                course=lesson.course,
                organization=membership.organization,
                is_cancelled=False
            )
        except Enrollment.DoesNotExist:
            raise PermissionDenied("Invalid Enrollment")

        progress = ProgressService.mark_lesson_completed(enrollment, lesson)

        return Response(
            {
                "message": "Lesson completed",
                "progress": progress.percentage
            },
            status=status.HTTP_200_OK
        )





















# owns_course
# can_view_course
# can_create_course
# can_edit_course
# can_delete_course
# can_publish_course
# is_enrolled_in
# can_view_lesson
# can_edit_lesson
# can_delete_lesson
# can_enroll_in
# can_view_enrollments_for









# class LessonViewSet(viewsets.ModelViewSet):
#     queryset = Lesson.objects.all()
#     serializer_class = LessonSerializer

#     def get_queryset(self):
#         membership = self.request.membership
























# class LessonViewset(viewsets.ModelViewSet):
#     queryset = Lesson.objects.all()

#     def perform_create(self, serializer):
#         course_id = self.request.data.get("course")

#         try:
#             course = Course.objects.get(
#                 pk=course_id
#             )
#         except Course.DoesNotExist:
#             raise NotFound("Course not found")

#         if not self.request.membership.can_edit_course(course):
#             raise PermissionDenied()

#         serializer.save(course=course)

#     def retrieve(self, request, *args, **kwargs):
#         lesson = self.get_object()
#         membership = request.membership
        
#         # if membership.is_student():
#         #     if not membership.is_student_enrolled(lesson.course):
#         #         raise PermissionDenied("You are not enrolled in this course")

#         # if membership.is_instructor():
#         #     if not membership.owns_course(course):
#         #         raise PermissionDenied("You can only access your own courses")

#         serializer = LessonSerializer(lesson)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#         # return super().retrieve(request, *args, **kwargs)


#     @action(detail=True, methods=["put"])
#     def update_lesson(self, request, pk=None):
#         membership = request.membership
#         course = self.get_object()


#         if membership.is_instructor() and not membership.owns_course(course):
#             raise PermissionDenied("You can only update your own courses")

#         serializer = LessonUpdateSerializer(lesson, data=request.data)

#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)


#     @action(detail=True, methods=["patch"])
#     def partial_update_lesson(self, request, pk=None):
#         course = self.get_object()
#         membership = request.membership
#         lesson_id = request.query_params.get("lesson_id")

#         if not lesson_id:
#             raise ValidationError("lesson_id is required")

#         lesson = self._get_lesson(course, lesson_id, membership)

#         if membership.is_instructor() and not membership.owns_course(course):
#             raise PermissionDenied("You can only update your own courses")

#         serializer = LessonPartialUpdateSerializer(lesson, data=request.data, partial=True)

#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)


#     @action(detail=True, methods=["delete"])
#     def delete_lesson(self, request, pk=None):
#         course = self.get_object()
#         membership = request.membership
#         lesson_id = request.query_params.get("lesson_id")

#         if not lesson_id:
#             raise ValidationError("lesson_id is required")
        
#         lesson = self._get_lesson(course, lesson_id, membership)

#         if membership.is_instructor() and not membership.owns_course(course):
#             raise PermissionDenied("You can only delete your own lessons")
        
#         lesson.delete()

#         return Response(
#             {
#                 "message": f"Lesson deleted"
#             },
#             status=status.HTTP_204_NO_CONTENT
#         )


















# class LessonViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated, LessonPermission]


#     def get_serializer_class(self):
#         if self.action == 'create':
#             return LessonCreateSerializer
#         return LessonSerializer


#     def get_queryset(self):
#         course_pk = self.kwargs.get("course_pk")
#         membership = self.request.membership

#         queryset = Lesson.objects.filter(course_id=course_pk)

#         if membership.is_student():
#             is_enrolled = Enrollment.objects.filter(
#                 student=membership,
#                 course_id=course_pk,
#                 is_cancelled=False
#             ).exists()

#             if not is_enrolled:
#                 raise PermissionDenied("You are not enrolled in this course")


#         if membership.is_instructor():
#             queryset = queryset.filter(
#                 course__instructor=membership
#             )

#         return queryset


# class EnrollmentViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
#     permission_classes = [IsAuthenticated, EnrollmentPermission]
#     serializer_class = EnrollmentSerializer

#     def get_queryset(self):
#         membership = self.request.membership

#         if membership.is_student():
#             return Enrollment.objects.filter(
#                 student=membership,
#                 organization=membership.organization
#             )

#         if membership.is_instructor():
#             return Enrollment.objects.filter(
#                 course__instructor=membership,
#                 organization=membership.organization
#             )

#         return Enrollment.objects.none()