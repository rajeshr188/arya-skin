import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^\+?[0-9 ()-]{7,24}$",
    message="Enter a valid phone number using digits and optional +, spaces, or hyphens.",
)


class AppointmentEnquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        SCHEDULED = "scheduled", "Scheduled"
        CLOSED = "closed", "Closed"
        SPAM = "spam", "Spam"

    class TimePreference(models.TextChoices):
        NO_PREFERENCE = "no_preference", "No preference"
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    clinic = models.ForeignKey(
        "clinics.ClinicPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appointment_enquiries",
    )
    clinic_name = models.CharField(
        max_length=255,
        editable=False,
        help_text="Snapshot retained if the editorial clinic page is later removed.",
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=25, validators=[phone_validator])
    email = models.EmailField(blank=True)
    preferred_date = models.DateField()
    time_preference = models.CharField(
        max_length=20,
        choices=TimePreference.choices,
        default=TimePreference.NO_PREFERENCE,
    )
    consent_to_contact = models.BooleanField(default=False)
    consent_version = models.CharField(max_length=40, editable=False)
    source_path = models.CharField(max_length=255, blank=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    staff_note = models.TextField(
        blank=True,
        max_length=1000,
        help_text=(
            "Administrative follow-up only. Do not store diagnosis or detailed "
            "clinical notes here."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "appointment enquiry"
        verbose_name_plural = "appointment enquiries"

    def __str__(self):
        created = self.created_at.date().isoformat() if self.created_at else "unsaved"
        return f"{self.name} — {self.clinic_name} — {created}"

    def clean(self):
        super().clean()
        errors = {}
        if self.preferred_date and self.preferred_date < timezone.localdate():
            errors["preferred_date"] = "Choose today or a future date."
        if not self.consent_to_contact:
            errors["consent_to_contact"] = "Consent is required before submitting."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.clinic_id and not self.clinic_name:
            self.clinic_name = self.clinic.title
        super().save(*args, **kwargs)
