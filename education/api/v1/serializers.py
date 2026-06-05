from rest_framework import serializers
from education.services.feedback_service import FeedbackService
from rest_framework.exceptions import NotFound
from django.db import IntegrityError
from education.models import (
    Course,
    Lesson,
    Enrollment,
    Progress,
    Feedback
)
from organization.models import Membership
from django.db.models import Max
from rest_framework.exceptions import PermissionDenied
from django.db import transaction


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "organization",
            "title",
            "description",
            "type",
            "is_active",
            "status",
            "published_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "instructor",
            "organization",
            "published_at",
        ]


class CourseCreateSerializer(serializers.ModelSerializer):
    instructor_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "type",
            "description",
            "instructor_id",
            "is_active"
        ]
        read_only_fields = [
            "id",
            "is_active",
        ]

    def validate(self, attrs):
        """
        Validating data only for OWNER and INSTRUCTOR roles
        ADMIN and STUDENT will be blocked for this API througn permissions
        """

        request = self.context["request"]
        membership = request.membership

        if membership.is_owner:
            instructor_id = attrs.pop("instructor_id", None)

            if not instructor_id:
                raise serializers.ValidationError("Owner is required to assign any instructor")

            try:
                instructor = Membership.objects.get(
                    pk=instructor_id,
                    organization=membership.organization,
                    role=Membership.Role.INSTRUCTOR,
                    is_active=True
                )
            except Membership.DoesNotExist:
                raise serializers.ValidationError("Invalid Instructor")

            attrs["instructor"] = instructor

        elif membership.is_instructor:
            if "instructor_id" in attrs:
                raise serializers.ValidationError("Instructor cannot assign Instructor")

            attrs["instructor"] = membership
            

        return attrs


class CourseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "type"
        ]

    def validate(self, attrs):
        title = attrs.get("title")

        if title is not None and len(title.strip()) < 3:
            raise serializers.ValidationError("Title must contain more than 3 characters")

        return attrs


class LessonSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="course.title", read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content",
            "video_link",
            "course"
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        membership = self.context.get("membership")

        if membership.is_staff:
            return data

        if membership.is_student:
            if not membership.is_enrolled_in(instance.course):
                data.pop("content", None)
                data.pop("video_link", None)
            return data

        return data


class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "video_link"
        ]

    def validate(self, attrs):
        if not attrs.get("content") and not attrs.get("video_link"):
            raise serializers.ValidationError("Lesson must have either content or video_link")

        return attrs


    def create(self, validated_data):
        request = self.context["request"]
        membership = request.membership
        course = self.context.get("course")

        if membership.is_instructor:
            if not membership.owns_course(course):
                raise PermissionDenied("You can only create lessons for your own courses")

        last_order = Lesson.objects.filter(course_id=course.pk).aggregate(
            max_order=Max("order")
        )["max_order"]

        order = (last_order or 0) + 1

        return Lesson.objects.create(
            course=course,
            order=order,
            **validated_data
        )


class LessonUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "video_link"
        ]

    def validate(self, attrs):
        if not attrs.get("content") and not attrs.get("video_link"):
            raise serializers.ValidationError("Lesson must have either content or video_link")

        return attrs


class LessonPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "content",
            "video_link"
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "student",
            "enrolled_at",
            "is_cancelled"
        ]

class EnrollmentCreateSerializer(serializers.Serializer):

    def create(self, validated_data):
        request = self.context["request"]
        membership = request.membership
        course_pk = self.context["view"].kwargs.get("pk")

        if not membership.is_student:
            raise PermissionDenied("Only students can enroll in courses")

        try:
            course = Course.objects.get(
                id=course_pk,
                organization=membership.organization,
                is_active=True,
                status=Course.Status.PUBLISHED
            )
        except Course.DoesNotExist:
            raise NotFound("Course not found")

        enrollment, created = Enrollment.objects.get_or_create(
            student=membership,
            course=course,
            defaults={"organization": membership.organization}
        )

        if not created:
            raise serializers.ValidationError("Already enrolled in this course")

        Progress.objects.create(enrollment=enrollment)

        return enrollment


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "rating",
            "comment",
            "student",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        membership = request.membership

        if membership.is_student:
            data.pop("student", None)

        return data



class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "rating",
            "comment",
            "is_approved",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "student",
            "is_approved",
            "created_at"
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        membership = request.membership
        course = self.context["course"]

        if Feedback.objects.filter(course=course, student=membership).exists():
            raise serializers.ValidationError(
                "You have already submitted feedback for this course"
            )

        if not membership.can_give_feedback(course):
            raise PermissionDenied("You cannot give feedback")

        attrs["course_id"] = course.id

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        validated_data["student"] = request.membership
        validated_data["organization"] = request.membership.organization
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("You have already submitted feedback for this course")


class LessonPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = []

    def validate(self, attrs):
        request = self.context.get("request")
        membership = request.membership
        lesson = self.context.get("lesson")

        course = lesson.course

        if membership.is_instructor and not membership.owns_course(course):
            raise serializers.ValidationError(
                "You can only publish lessons of your own course"
            )

        if not course.is_published:
            raise serializers.ValidationError(
                "Cannot publish lesson of unpublished course"
            )

        if lesson.is_published:
            raise serializers.ValidationError(
                "Lesson is already published"
            )

        return attrs