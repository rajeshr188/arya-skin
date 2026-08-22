import re

from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page

from .blocks import ContentStreamBlock


class HomePage(Page):
    """The single site root with deliberately structured marketing sections."""

    hero_eyebrow = models.CharField(max_length=120, blank=True)

    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="A short, factual introduction. Do not add unverified credentials.",
    )
    concerns_heading = models.CharField(max_length=160, blank=True)
    doctor_section_heading = models.CharField(max_length=160, blank=True)
    clinic_section_heading = models.CharField(max_length=160, blank=True)
    blog_section_heading = models.CharField(max_length=160, blank=True)
    faq_heading = models.CharField(max_length=160, blank=True)
    final_cta_heading = models.CharField(max_length=160, blank=True)
    final_cta_text = models.TextField(blank=True)

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow"),
                FieldPanel("introduction"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("concerns_heading"),
                FieldPanel("doctor_section_heading"),
                FieldPanel("clinic_section_heading"),
                FieldPanel("blog_section_heading"),
            ],
            heading="Section headings",
        ),
        MultiFieldPanel(
            [FieldPanel("faq_heading"), InlinePanel("faqs", label="Homepage FAQ")],
            heading="FAQs",
        ),
        MultiFieldPanel(
            [FieldPanel("final_cta_heading"), FieldPanel("final_cta_text")],
            heading="Final call to action",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        from clinics.models import ClinicPage
        from doctors.models import DoctorPage
        from treatments.models import TreatmentPage
        from blog.models import BlogPage

        context = super().get_context(request, *args, **kwargs)
        context["doctor_page"] = DoctorPage.objects.live().public().first()
        context["clinics"] = ClinicPage.objects.live().public().order_by("path")
        context["featured_treatments"] = (
            TreatmentPage.objects.live()
            .public()
            .filter(feature_on_homepage=True)
            .order_by("title")[:8]
        )
        context["contact_page"] = ContactPage.objects.live().public().first()
        context["latest_articles"] = (
            BlogPage.objects.live()
            .public()
            .select_related("featured_image", "author")
            .prefetch_related("categories")
            .order_by("-first_published_at", "-last_published_at")[:3]
        )
        return context


class HomePageFAQ(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = RichTextField(
        features=["bold", "italic", "ol", "ul", "link"]
    )

    panels = [FieldPanel("question"), FieldPanel("answer")]


class ContactPage(Page):
    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    body = StreamField(ContentStreamBlock(), blank=True, use_json_field=True)

    parent_page_types = ["website.HomePage"]
    subpage_types = []
    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        from clinics.models import ClinicPage

        context = super().get_context(request, *args, **kwargs)
        context["clinics"] = ClinicPage.objects.live().public().order_by("path")
        return context


class StandardPage(Page):
    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    body = StreamField(ContentStreamBlock(), blank=True, use_json_field=True)

    parent_page_types = ["website.HomePage"]
    subpage_types = ["website.StandardPage"]

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("body"),
    ]


@register_setting(icon="cog")
class SiteSettings(BaseSiteSetting):
    """Editable site-wide data; branch-specific facts belong to ClinicPage."""

    site_title = models.CharField(
        max_length=140, default="Dr. Naresh Rathod - Dermatologist"
    )
    doctor_name = models.CharField(max_length=100, default="Dr. Naresh Rathod")
    professional_title = models.CharField(
        max_length=120, default="Dermatologist and Cosmetologist"
    )
    location_summary = models.CharField(
        max_length=255,
        default=(
            "Dolphin Derma Care - Sitapura | "
            "Arya Skin and Hair Clinic - Chaksu | Jaipur"
        ),
        help_text="A short display summary, not a substitute for clinic addresses.",
    )
    primary_phone = models.CharField(
        max_length=30,
        blank=True,
        help_text="Verified site-wide fallback only. Prefer branch-specific numbers.",
    )
    default_whatsapp = models.CharField(
        max_length=30,
        blank=True,
        help_text="Verified site-wide fallback only. Prefer branch-specific numbers.",
    )
    default_email = models.EmailField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    default_social_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    medical_disclaimer = models.TextField(
        default=(
            "This information is intended for general educational purposes and "
            "does not replace consultation with a qualified medical professional."
        )
    )
    analytics_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Enable only after account ownership, the privacy notice, consent "
            "behavior, and the analytics configuration have been approved."
        ),
    )
    google_analytics_id = models.CharField(max_length=30, blank=True)
    google_tag_manager_id = models.CharField(max_length=30, blank=True)
    google_search_console_verification = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Content value from Google's HTML verification meta tag. "
            "Do not paste the complete tag."
        ),
    )

    def clean(self):
        super().clean()
        errors = {}
        ga_id = self.google_analytics_id.strip().upper()
        gtm_id = self.google_tag_manager_id.strip().upper()
        verification = self.google_search_console_verification.strip()

        if ga_id and not re.fullmatch(r"G-[A-Z0-9]+", ga_id):
            errors["google_analytics_id"] = "Enter a GA4 ID such as G-XXXXXXXXXX."
        if gtm_id and not re.fullmatch(r"GTM-[A-Z0-9]+", gtm_id):
            errors["google_tag_manager_id"] = (
                "Enter a Tag Manager container ID such as GTM-XXXXXXX."
            )
        if ga_id and gtm_id:
            message = "Configure GA4 directly or Tag Manager, not both."
            errors["google_analytics_id"] = message
            errors["google_tag_manager_id"] = message
        if self.analytics_enabled and not (ga_id or gtm_id):
            errors["analytics_enabled"] = (
                "Add one approved GA4 or Tag Manager ID before enabling analytics."
            )
        if verification and not re.fullmatch(r"[A-Za-z0-9_-]+", verification):
            errors["google_search_console_verification"] = (
                "Enter only the verification content value, using letters, numbers, "
                "hyphens, or underscores."
            )
        if errors:
            raise ValidationError(errors)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site_title"),
                FieldPanel("doctor_name"),
                FieldPanel("professional_title"),
                FieldPanel("location_summary"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_phone"),
                FieldPanel("default_whatsapp"),
                FieldPanel("default_email"),
            ],
            heading="Default contact details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("instagram_url"),
                FieldPanel("facebook_url"),
                FieldPanel("youtube_url"),
                FieldPanel("linkedin_url"),
            ],
            heading="Social profiles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("default_social_image"),
                FieldPanel("medical_disclaimer"),
            ],
            heading="Site defaults",
        ),
        MultiFieldPanel(
            [
                FieldPanel("analytics_enabled"),
                FieldPanel("google_analytics_id"),
                FieldPanel("google_tag_manager_id"),
                FieldPanel("google_search_console_verification"),
            ],
            heading="Analytics",
            help_text=(
                "Only one analytics provider may be active. Tags remain blocked "
                "until a visitor opts in."
            ),
        ),
    ]
