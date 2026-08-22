import re
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index


class ClinicIndexPage(Page):
    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )

    parent_page_types = ["website.HomePage"]
    subpage_types = ["clinics.ClinicPage"]
    max_count = 1

    content_panels = Page.content_panels + [FieldPanel("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["clinics"] = ClinicPage.objects.child_of(self).live().public()
        return context


class ClinicPage(Page):
    """A real clinic location with branch-owned contact and local SEO facts."""

    doctor = models.ForeignKey(
        "doctors.DoctorPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clinic_pages",
    )
    locality = models.CharField(max_length=120)
    city = models.CharField(max_length=120, default="Jaipur")
    state = models.CharField(max_length=120, default="Rajasthan")
    postal_code = models.CharField(max_length=12, blank=True)
    address = models.TextField(
        blank=True,
        help_text="Verified street/building address. Do not repeat locality/city here.",
    )
    summary = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    phone = models.CharField(max_length=30, blank=True)
    phone_is_public = models.BooleanField(
        default=False,
        help_text="Enable only after confirming this number may be published.",
    )
    whatsapp = models.CharField(
        max_length=30,
        blank=True,
        help_text="Use a verified international number beginning with +.",
    )
    whatsapp_is_public = models.BooleanField(
        default=False,
        help_text="Enable only after confirming WhatsApp publication consent.",
    )
    doctor_availability = models.TextField(blank=True)
    google_maps_url = models.URLField(blank=True)
    google_business_profile_url = models.URLField(blank=True)
    google_place_id = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    nearby_landmark = models.CharField(max_length=255, blank=True)
    parking_information = models.TextField(blank=True)
    accessibility_information = models.TextField(blank=True)

    parent_page_types = ["clinics.ClinicIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("doctor"),
        FieldPanel("summary"),
        MultiFieldPanel(
            [
                FieldPanel("locality"),
                FieldPanel("address"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("postal_code"),
                FieldPanel("nearby_landmark"),
            ],
            heading="Address",
        ),
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("phone_is_public"),
                FieldPanel("whatsapp"),
                FieldPanel("whatsapp_is_public"),
            ],
            heading="Contact and publication consent",
        ),
        InlinePanel("opening_hours", label="Opening-hours entry"),
        FieldPanel("doctor_availability"),
        InlinePanel("services", label="Branch service"),
        InlinePanel("gallery_images", label="Clinic photograph"),
        MultiFieldPanel(
            [
                FieldPanel("google_maps_url"),
                FieldPanel("google_business_profile_url"),
                FieldPanel("google_place_id"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
            ],
            heading="Google and coordinates",
        ),
        MultiFieldPanel(
            [
                FieldPanel("parking_information"),
                FieldPanel("accessibility_information"),
            ],
            heading="Access information",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("locality"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.SearchField("summary"),
    ]

    def clean(self):
        super().clean()
        errors = {}
        if self.phone_is_public and not self.phone:
            errors["phone"] = "Enter a phone number before making it public."
        if self.whatsapp_is_public and not self.whatsapp:
            errors["whatsapp"] = "Enter a WhatsApp number before making it public."
        elif self.whatsapp_is_public and not self.whatsapp.strip().startswith("+"):
            errors["whatsapp"] = (
                "Use a verified international WhatsApp number beginning with +."
            )
        if errors:
            raise ValidationError(errors)

    @property
    def phone_uri(self):
        if not (self.phone_is_public and self.phone):
            return ""
        normalized = re.sub(r"[^0-9+]", "", self.phone)
        return f"tel:{normalized}"

    @property
    def whatsapp_url(self):
        if not (self.whatsapp_is_public and self.whatsapp):
            return ""
        normalized = re.sub(r"\D", "", self.whatsapp)
        message = (
            "Hello, I would like to request an appointment with "
            "Dr. Naresh Rathod at " + self.title + "."
        )
        return f"https://wa.me/{normalized}?text={quote(message)}"

    @property
    def formatted_address(self):
        parts = [self.address, self.locality, self.city, self.state, self.postal_code]
        return ", ".join(part.strip() for part in parts if part and part.strip())


class ClinicOpeningHours(Orderable):
    DAYS = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]

    page = ParentalKey(
        ClinicPage, on_delete=models.CASCADE, related_name="opening_hours"
    )
    day = models.CharField(max_length=9, choices=DAYS)
    opens_at = models.TimeField(null=True, blank=True)
    closes_at = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    appointment_only = models.BooleanField(default=False)
    notes = models.CharField(max_length=160, blank=True)

    panels = [
        FieldPanel("day"),
        FieldPanel("opens_at"),
        FieldPanel("closes_at"),
        FieldPanel("is_closed"),
        FieldPanel("appointment_only"),
        FieldPanel("notes"),
    ]


class ClinicService(Orderable):
    page = ParentalKey(ClinicPage, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=160)
    notes = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("name"), FieldPanel("notes")]


class ClinicImage(Orderable):
    page = ParentalKey(
        ClinicPage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        get_image_model_string(), on_delete=models.CASCADE, related_name="+"
    )
    alt_text = models.CharField(
        max_length=255,
        help_text="Describe the visible clinic scene for people who cannot see it.",
    )
    caption = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("image"), FieldPanel("alt_text"), FieldPanel("caption")]
