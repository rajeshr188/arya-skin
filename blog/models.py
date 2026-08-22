from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from website.blocks import ContentStreamBlock


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("description")]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "blog categories"

    def __str__(self):
        return self.name


@register_snippet
class BlogAuthor(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=160)
    biography = models.TextField(blank=True, max_length=800)
    doctor_page = models.ForeignKey(
        "doctors.DoctorPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_author_profiles",
    )
    portrait = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    portrait_alt_text = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("biography"),
        FieldPanel("doctor_page"),
        FieldPanel("portrait"),
        FieldPanel("portrait_alt_text"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.role}"

    def clean(self):
        super().clean()
        if self.portrait and not self.portrait_alt_text.strip():
            raise ValidationError(
                {"portrait_alt_text": "Describe the portrait before using it."}
            )


class BlogIndexPage(Page):
    introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    posts_per_page = models.PositiveSmallIntegerField(
        default=9,
        validators=[MinValueValidator(3), MaxValueValidator(24)],
    )

    parent_page_types = ["website.HomePage"]
    subpage_types = ["blog.BlogPage"]
    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("posts_per_page"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        articles = (
            BlogPage.objects.child_of(self)
            .live()
            .public()
            .select_related("featured_image", "author")
            .prefetch_related("categories")
            .order_by("-first_published_at", "-last_published_at")
        )
        public_category_ids = articles.values_list("categories__id", flat=True)
        context["categories"] = BlogCategory.objects.filter(
            id__in=public_category_ids
        ).distinct()
        selected_category = None
        category_slug = request.GET.get("category", "").strip()
        if category_slug:
            selected_category = BlogCategory.objects.filter(slug=category_slug).first()
            if selected_category:
                articles = articles.filter(categories=selected_category)

        context["selected_category"] = selected_category
        context["articles"] = Paginator(articles.distinct(), self.posts_per_page).get_page(
            request.GET.get("page")
        )
        return context


class BlogPage(Page):
    class ReviewStatus(models.TextChoices):
        NOT_REVIEWED = "not_reviewed", "Not reviewed"
        AWAITING_REVIEW = "awaiting_review", "Awaiting review"
        REVIEWED = "reviewed", "Reviewed"

    excerpt = models.TextField(max_length=400)
    featured_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    featured_image_alt_text = models.CharField(max_length=255, blank=True)
    body = StreamField(ContentStreamBlock(), blank=True, use_json_field=True)
    author = models.ForeignKey(
        BlogAuthor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles_authored",
    )
    review_status = models.CharField(
        max_length=24,
        choices=ReviewStatus.choices,
        default=ReviewStatus.NOT_REVIEWED,
    )
    reviewed_by = models.ForeignKey(
        BlogAuthor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles_reviewed",
    )
    reviewed_on = models.DateField(null=True, blank=True)
    review_due_on = models.DateField(null=True, blank=True)
    categories = ParentalManyToManyField(
        BlogCategory,
        blank=True,
        related_name="blog_pages",
    )
    related_treatments = ParentalManyToManyField(
        "treatments.TreatmentPage",
        blank=True,
        related_name="related_blog_pages",
    )

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("excerpt"),
                FieldPanel("featured_image"),
                FieldPanel("featured_image_alt_text"),
                FieldPanel("categories"),
            ],
            heading="Article summary",
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("review_status"),
                FieldPanel("reviewed_by"),
                FieldPanel("reviewed_on"),
                FieldPanel("review_due_on"),
            ],
            heading="Authorship and medical review",
        ),
        InlinePanel("sources", label="Source"),
        FieldPanel("related_treatments"),
        InlinePanel("related_article_links", label="Related article"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("body"),
    ]

    def clean(self):
        super().clean()
        errors = {}
        if self.featured_image and not self.featured_image_alt_text.strip():
            errors["featured_image_alt_text"] = (
                "Describe the featured image before using it."
            )
        if self.reviewed_on and self.reviewed_on > timezone.localdate():
            errors["reviewed_on"] = "The review date cannot be in the future."
        if self.review_status == self.ReviewStatus.REVIEWED:
            if not self.reviewed_by:
                errors["reviewed_by"] = "Choose the person who performed the review."
            if not self.reviewed_on:
                errors["reviewed_on"] = "Enter the completed review date."
        elif self.reviewed_on:
            errors["reviewed_on"] = (
                "A completed review date requires the Reviewed status."
            )
        if self.review_due_on and self.reviewed_on:
            if self.review_due_on <= self.reviewed_on:
                errors["review_due_on"] = "The next review must be after the review date."
        if errors:
            raise ValidationError(errors)

    def publication_errors(self):
        errors = []
        if not self.author:
            errors.append("an identified author")
        if self.featured_image and not self.featured_image_alt_text.strip():
            errors.append("featured-image alternative text")
        if not self.body:
            errors.append("article body content")
        if self.review_status != self.ReviewStatus.REVIEWED:
            errors.append("Reviewed status")
        if not self.reviewed_by:
            errors.append("an identified medical reviewer")
        if not self.reviewed_on:
            errors.append("a completed review date")
        elif self.reviewed_on > timezone.localdate():
            errors.append("a non-future review date")
        if self.review_due_on and self.reviewed_on:
            if self.review_due_on <= self.reviewed_on:
                errors.append("a next-review date after the completed review")
        if not self.pk or not self.sources.exists():
            errors.append("at least one factual source")
        return errors

    def save(self, *args, **kwargs):
        if self.live:
            errors = self.publication_errors()
            if errors:
                raise ValidationError(
                    "Cannot publish this medical article without " + ", ".join(errors) + "."
                )
        return super().save(*args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["author_profile"] = self._public_doctor_for(self.author)
        context["reviewer_profile"] = self._public_doctor_for(self.reviewed_by)
        context["related_treatment_pages"] = (
            self.related_treatments.live().public().order_by("title")
        )
        related_ids = self.related_article_links.values_list(
            "related_article_id", flat=True
        )
        context["related_articles"] = (
            BlogPage.objects.live()
            .public()
            .filter(id__in=related_ids)
            .exclude(id=self.id)
            .select_related("featured_image", "author")
            .prefetch_related("categories")
            .order_by("-first_published_at")
        )
        return context

    @staticmethod
    def _public_doctor_for(person):
        if not person or not person.doctor_page_id:
            return None
        from doctors.models import DoctorPage

        return DoctorPage.objects.live().public().filter(id=person.doctor_page_id).first()


class BlogSource(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name="sources")
    title = models.CharField(max_length=255)
    publisher = models.CharField(max_length=160, blank=True)
    url = models.URLField()
    accessed_on = models.DateField(null=True, blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("publisher"),
        FieldPanel("url"),
        FieldPanel("accessed_on"),
    ]


class BlogRelatedArticle(Orderable):
    page = ParentalKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name="related_article_links",
    )
    related_article = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name="linked_from_articles",
    )

    panels = [FieldPanel("related_article")]

    def clean(self):
        super().clean()
        if self.page_id and self.related_article_id == self.page_id:
            raise ValidationError(
                {"related_article": "An article cannot be related to itself."}
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["page", "related_article"],
                name="unique_related_blog_article",
            )
        ]
