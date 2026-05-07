# from rest_framework.exceptions import ValidationError, PermissionDenied
# from education.models import Enrollment, Progress
# from organization.models import Membership


# class EnrollmentService:

#     @staticmethod
#     def enroll_student(membership, course):

#         if not membership.is_student():
#             raise PermissionDenied("Only students can enroll in courses")

#         if course.organization_id != membership.organization_id:
#             raise ValidationError("Cross organization enrollment not allowed")

#         enrollment, created = Enrollment.objects.get_or_create(
#             student=membership,
#             course=course,
#             defaults={
#                 "organization": membership.organization
#             }
#         )

#         if not created:
#             raise ValidationError("Already enrolled in this course")


#         Progress.objects.create(enrollment=enrollment)

#         return enrollment