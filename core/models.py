from django.db import models
from django.utils import timezone


class TimeStampModel(models.Model):
    """
    An abstract/base model that provides automatic
    created_at and updated_at timestamp fields
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProfileBaseModel(models.Model):
    """
    An abstract/base model that represents a profile linked to a User
    Tracks basic information fields
    """

    membership = models.OneToOneField("organization.Membership", on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    cnic = models.CharField(max_length=15, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="profile_pictures/")
    joined_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        full_name = f"{self.membership.user.first_name} {self.membership.user.last_name}"
        return full_name

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """
    Abstract model for tracking publishment flow of the content
    Contains methods like mark_published, mark_failed to automatically update the status
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHING = "PUBLISHING", "Publishing"
        PUBLISHED = "PUBLISHED", "Published"
        FAILED = "FAILED", "Failed"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    failure_cause = models.TextField(null=True, blank=True)

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    class Meta:
        abstract = True


    def publish_lessons(self):
        pass


    def mark_published(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.status_changed_at = timezone.now()
        self.failure_cause = None
        self.save()

        self.publish_lessons()

    def mark_failed(self, message):
        self.status = self.Status.FAILED
        self.status_changed_at = timezone.now()
        self.failure_cause = message
        self.save()