import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from core.models import ProfileBaseModel


class Owner(ProfileBaseModel):
    """
    Admin Profile
    Inherits common fields from ProfileBaseModel
    Also keeps the creation and modification date from TimeStampModel
    """
    
    pass

    def __str__(self):
        return self.full_name


class Admin(ProfileBaseModel):
    """
    Admin Profile
    Inherits common fields from ProfileBaseModel
    Also keeps the creation and modification date from TimeStampModel
    """

    subjects = models.CharField(max_length=255, null=True, blank=True)
    managed_classes = models.CharField(max_length=100, null=True, blank=True)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Instructor(ProfileBaseModel):
    """
    Instructor Profile
    Inherits common fields from ProfileBaseModel
    Also keeps the creation and modification date from TimeStampModel
    """

    subjects = models.CharField(max_length=255, null=True, blank=True)
    assigned_classes = models.CharField(max_length=100, null=True, blank=True)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Student(ProfileBaseModel):
    """
    Student Profile
    Inherits common fields from ProfileBaseModel
    Also keeps the creation and modification date from TimeStampModel
    """

    class Section(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"

    grade = models.PositiveIntegerField(null=True, blank=True)
    section = models.CharField(max_length=1, choices=Section.choices, null=True, blank=True)
    roll_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.full_name


class AccountActivationToken(models.Model):
    """
    Generates a onetime activation token for user after signup
    if used, the token will be expired
    Valid for 24 hours
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activation_token")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    @property
    def is_expired(self):
        if self.is_used:
            return True
        return timezone.now() > self.expiration_date

    def mark_as_used(self):
        self.is_used = True
        self.expiration_date = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.token}"