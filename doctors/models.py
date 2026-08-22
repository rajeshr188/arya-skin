from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index


class DoctorPage(Page):
    """Structured professional profile for Dr. Naresh Rathod."""

    professional_title = models.CharField(max_length=160)
    portrait = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    biography = RichTextField(
        blank=True,
        features=["h2", "h3", "bold", "italic", "ol", "ul", "link"],
    )
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    experience_as_of_date = models.DateField(
        null=True,
        blank=True,
        help_text="Required whenever a years-of-experience claim is displayed.",
    )
    philosophy_of_care = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    professional_affiliations = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )

    parent_page_types = ["website.HomePage"]
    subpage_types = []
    max_count = 1

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("professional_title"), FieldPanel("portrait")],
            heading="Professional identity",
        ),
        FieldPanel("biography"),
        MultiFieldPanel(
            [FieldPanel("experience_years"), FieldPanel("experience_as_of_date")],
            heading="Experience claim",
        ),
        InlinePanel("qualifications", label="Qualification"),
        InlinePanel("registrations", label="Professional registration"),
        InlinePanel("specialties", label="Specialty"),
        InlinePanel("languages", label="Language"),
        InlinePanel("memberships", label="Professional membership"),
        FieldPanel("professional_affiliations"),
        FieldPanel("philosophy_of_care"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("professional_title"),
        index.SearchField("biography"),
    ]


class DoctorQualification(Orderable):
    page = ParentalKey(
        DoctorPage, on_delete=models.CASCADE, related_name="qualifications"
    )
    qualification = models.CharField(max_length=160)
    institution = models.CharField(max_length=255, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)

    panels = [
        FieldPanel("qualification"),
        FieldPanel("institution"),
        FieldPanel("year"),
    ]


class DoctorRegistration(Orderable):
    page = ParentalKey(
        DoctorPage, on_delete=models.CASCADE, related_name="registrations"
    )
    authority = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)
    registration_year = models.PositiveSmallIntegerField(null=True, blank=True)

    panels = [
        FieldPanel("authority"),
        FieldPanel("registration_number"),
        FieldPanel("registration_year"),
    ]


class DoctorSpecialty(Orderable):
    page = ParentalKey(
        DoctorPage, on_delete=models.CASCADE, related_name="specialties"
    )
    name = models.CharField(max_length=120)

    panels = [FieldPanel("name")]


class DoctorLanguage(Orderable):
    page = ParentalKey(
        DoctorPage, on_delete=models.CASCADE, related_name="languages"
    )
    name = models.CharField(max_length=80)

    panels = [FieldPanel("name")]


class DoctorMembership(Orderable):
    page = ParentalKey(
        DoctorPage, on_delete=models.CASCADE, related_name="memberships"
    )
    organization = models.CharField(max_length=255)
    membership_detail = models.CharField(max_length=255, blank=True)

    panels = [FieldPanel("organization"), FieldPanel("membership_detail")]
