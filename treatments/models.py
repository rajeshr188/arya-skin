from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from website.blocks import ContentStreamBlock


@register_snippet
class TreatmentCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "treatment categories"

    def __str__(self):
        return self.name


class TreatmentIndexPage(Page):
    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )

    parent_page_types = ["website.HomePage"]
    subpage_types = ["treatments.TreatmentPage"]
    max_count = 1

    content_panels = Page.content_panels + [FieldPanel("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["treatments"] = TreatmentPage.objects.child_of(self).live().public()
        return context


class TreatmentPage(Page):
    category = models.ForeignKey(
        TreatmentCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="treatment_pages",
    )
    doctor = models.ForeignKey(
        "doctors.DoctorPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="treatment_pages",
    )
    featured_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    summary = models.TextField(max_length=500)
    overview = RichTextField(
        blank=True,
        features=["h2", "h3", "bold", "italic", "ol", "ul", "link"],
    )
    symptoms = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    common_causes = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    diagnosis = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    when_to_consult = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    treatment_approaches = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    what_to_expect = RichTextField(
        blank=True,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    body = StreamField(ContentStreamBlock(), blank=True, use_json_field=True)
    available_at_clinics = ParentalManyToManyField(
        "clinics.ClinicPage",
        blank=True,
        related_name="available_treatment_pages",
    )
    feature_on_homepage = models.BooleanField(
        default=False,
        help_text="Feature only after this page and its medical content are approved.",
    )

    parent_page_types = ["treatments.TreatmentIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("doctor"),
                FieldPanel("featured_image"),
                FieldPanel("summary"),
                FieldPanel("feature_on_homepage"),
            ],
            heading="Summary",
        ),
        FieldPanel("overview"),
        FieldPanel("symptoms"),
        FieldPanel("common_causes"),
        FieldPanel("diagnosis"),
        FieldPanel("when_to_consult"),
        FieldPanel("treatment_approaches"),
        FieldPanel("what_to_expect"),
        FieldPanel("body"),
        InlinePanel("faqs", label="Treatment FAQ"),
        FieldPanel("available_at_clinics"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("overview"),
        index.SearchField("symptoms"),
        index.SearchField("common_causes"),
        index.SearchField("body"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["doctor_page"] = (
            self.doctor
            if self.doctor and self.doctor.live and not self.doctor.get_view_restrictions()
            else None
        )
        context["available_clinics"] = (
            self.available_at_clinics.live().public().order_by("path")
        )
        return context


class TreatmentFAQ(Orderable):
    page = ParentalKey(TreatmentPage, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = RichTextField(
        features=["bold", "italic", "ol", "ul", "link"]
    )

    panels = [FieldPanel("question"), FieldPanel("answer")]
