from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from education.models import Course



class CourseService:

    @staticmethod
    def create_course(membership, validated_data):
        try:
            return Course.objects.create(
                organization=membership.organization,
                **validated_data
            )
        except IntegrityError:
            raise ValidationError("Course with this title already exists for this instructor")


    @staticmethod
    def update_course(membership, course, serializer):

        if membership.is_instructor and not membership.owns_course(course):
            raise ValidationError("You can only update your own courses")

        if course.status != Course.Status.DRAFT:
            raise ValidationError("You cannot update an already published course")

        serializer.save()


    @staticmethod
    def get_courses_for_membership(membership):
        
        queryset = Course.objects.filter(
            organization=membership.organization,
            is_active=True
        )

        if membership.is_instructor:
            return queryset.filter(instructor=membership)
        
        if membership.is_owner:
            return queryset

        return Course.objects.none()


    @staticmethod
    def destroy_course(membership, instance):

        if membership.is_instructor and not membership.owns_course(instance):
            raise ValidationError("You can only delete your own courses")

        if instance.status == Course.Status.PUBLISHED:
            raise ValidationError("Published courses cannot be deleted")

        instance.delete()


    @staticmethod
    def publish_course(membership, course):

        if membership.is_instructor and not membership.owns_course(course):
            raise ValidationError("You can only publish your own courses")

        if course.status != Course.Status.DRAFT:
            raise ValidationError("Only draft courses can be published")

        if not course.lessons.exists():
            raise ValidationError("Course cannot be published without any lesson")

        course.mark_published()