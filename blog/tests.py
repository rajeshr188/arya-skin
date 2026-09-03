from datetime import timedelta
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from doctors.models import DoctorPage
from treatments.models import TreatmentIndexPage, TreatmentPage
from website.models import HomePage

from .models import (
    BlogAuthor,
    BlogCategory,
    BlogIndexPage,
    BlogPage,
    BlogRelatedArticle,
    BlogSource,
)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class BlogEditorialTests(TestCase):
    def setUp(self):
        self.index = BlogIndexPage.objects.get()
        self.author = BlogAuthor.objects.create(
            name="Test Author",
            role="Test health writer",
        )
        self.reviewer = BlogAuthor.objects.create(
            name="Test Reviewer",
            role="Test medical reviewer",
        )

    def make_article(
        self,
        title,
        *,
        slug=None,
        category=None,
        reviewed=True,
        with_source=True,
    ):
        article = BlogPage(
            title=title,
            slug=slug or title.lower().replace(" ", "-"),
            excerpt=f"Automated-test excerpt for {title}.",
            body=[("rich_text", f"<p>Reviewed test content for {title}.</p>")],
            author=self.author,
            review_status=(
                BlogPage.ReviewStatus.REVIEWED
                if reviewed
                else BlogPage.ReviewStatus.AWAITING_REVIEW
            ),
            reviewed_by=self.reviewer if reviewed else None,
            reviewed_on=timezone.localdate() if reviewed else None,
            live=False,
            has_unpublished_changes=True,
        )
        self.index.add_child(instance=article)
        if category:
            article.categories.add(category)
        if with_source:
            BlogSource.objects.create(
                page=article,
                title="Test medical source",
                publisher="Test publisher",
                url="https://example.com/test-source",
                accessed_on=timezone.localdate(),
            )
        article.save_revision()
        return article

    def publish_index(self):
        self.index.save_revision().publish()
        self.index.refresh_from_db()

    def publish_article(self, article):
        article.save_revision().publish()
        article.refresh_from_db()
        return article

    def test_empty_blog_container_is_seeded_as_a_draft(self):
        self.assertFalse(self.index.live)
        self.assertEqual(self.index.slug, "blog")
        self.assertEqual(self.index.get_parent().specific, HomePage.objects.get())
        self.assertEqual(BlogPage.objects.count(), 0)
        self.assertEqual(BlogCategory.objects.count(), 0)
        self.assertEqual(self.client.get("/blog/").status_code, 404)

    def test_content_seed_is_dry_run_first_and_creates_illustrated_drafts(self):
        call_command("seed_treatment_drafts", execute=True)

        dry_run_output = StringIO()
        call_command("seed_blog_drafts", stdout=dry_run_output)

        self.assertIn("would_create_blog_drafts=3", dry_run_output.getvalue())
        self.assertIn("would_import_blog_illustrations=3", dry_run_output.getvalue())
        self.assertEqual(BlogPage.objects.count(), 0)

        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            output = StringIO()
            call_command("seed_blog_drafts", execute=True, stdout=output)

            self.index.refresh_from_db()
            articles = BlogPage.objects.order_by("slug")
            self.assertFalse(self.index.live)
            self.assertIn("general education", self.index.introduction)
            self.assertEqual(articles.count(), 3)
            self.assertEqual(BlogCategory.objects.count(), 3)
            for article in articles:
                with self.subTest(article=article.slug):
                    self.assertFalse(article.live)
                    self.assertFalse(article.show_in_menus)
                    self.assertEqual(
                        article.review_status,
                        BlogPage.ReviewStatus.AWAITING_REVIEW,
                    )
                    self.assertIsNone(article.author)
                    self.assertIsNone(article.reviewed_by)
                    self.assertIsNone(article.reviewed_on)
                    self.assertTrue(article.featured_image)
                    self.assertTrue(article.featured_image_alt_text)
                    self.assertGreater(len(article.body), 5)
                    self.assertGreaterEqual(article.sources.count(), 2)
                    self.assertEqual(article.related_treatments.count(), 1)
                    self.assertIn("an identified author", article.publication_errors())
                    self.assertIn("Reviewed status", article.publication_errors())
                    self.assertNotIn(
                        "at least one factual source", article.publication_errors()
                    )
                    self.assertEqual(self.client.get(article.url).status_code, 404)

            self.assertIn("blog_drafts_created=3", output.getvalue())
            self.assertIn("blog_illustrations_imported=3", output.getvalue())
            self.assertIn(
                "author_and_medical_review_required=true", output.getvalue()
            )

            rerun_output = StringIO()
            call_command("seed_blog_drafts", execute=True, stdout=rerun_output)
            self.assertIn("blog_drafts_unchanged=3", rerun_output.getvalue())
            self.assertEqual(BlogPage.objects.count(), 3)

    def test_content_seed_refuses_a_partial_existing_set(self):
        self.index.add_child(
            instance=BlogPage(
                title="Existing acne article",
                slug="acne-treatment-takes-time",
                excerpt="Existing editorial content must not be overwritten.",
                live=False,
            )
        )

        with self.assertRaisesMessage(CommandError, "partial seed"):
            call_command("seed_blog_drafts", execute=True)

    def test_owner_approved_editorial_roles_are_assigned_without_review_claim(self):
        call_command("seed_treatment_drafts", execute=True)
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            call_command("seed_blog_drafts", execute=True)

            existing_person = BlogAuthor.objects.create(
                name="Dr. Naresh Rathod",
                role="Doctor",
                doctor_page=DoctorPage.objects.get(),
            )
            existing_article = BlogPage.objects.get(
                slug="acne-treatment-takes-time"
            )
            existing_article.author = existing_person
            existing_article.reviewed_by = existing_person
            existing_article.save(update_fields=("author", "reviewed_by"))

            dry_run_output = StringIO()
            call_command("assign_blog_editorial_roles", stdout=dry_run_output)
            self.assertIn(
                "would_assign_blog_editorial_roles=3",
                dry_run_output.getvalue(),
            )
            self.assertIn(
                "completed_medical_review=false",
                dry_run_output.getvalue(),
            )
            self.assertIn(
                "would_update_author_role=true",
                dry_run_output.getvalue(),
            )

            output = StringIO()
            call_command(
                "assign_blog_editorial_roles",
                execute=True,
                stdout=output,
            )

            person = BlogAuthor.objects.get(name="Dr. Naresh Rathod")
            self.assertEqual(person.role, "Dermatologist and Cosmetologist")
            self.assertEqual(person.doctor_page, DoctorPage.objects.get())
            for article in BlogPage.objects.all():
                with self.subTest(article=article.slug):
                    self.assertEqual(article.author, person)
                    self.assertEqual(article.reviewed_by, person)
                    self.assertEqual(
                        article.review_status,
                        BlogPage.ReviewStatus.AWAITING_REVIEW,
                    )
                    self.assertIsNone(article.reviewed_on)
                    self.assertIn("Reviewed status", article.publication_errors())
                    self.assertIn(
                        "a completed review date", article.publication_errors()
                    )

            self.assertIn("blog_editorial_roles_assigned=3", output.getvalue())
            self.assertIn("completed_medical_review=false", output.getvalue())

            rerun_output = StringIO()
            call_command(
                "assign_blog_editorial_roles",
                execute=True,
                stdout=rerun_output,
            )
            self.assertIn(
                "blog_editorial_roles_unchanged=3", rerun_output.getvalue()
            )

    def test_incomplete_article_can_be_saved_as_draft_but_not_published(self):
        article = BlogPage(
            title="Incomplete test draft",
            slug="incomplete-test-draft",
            excerpt="An intentionally incomplete automated-test draft.",
            live=False,
            has_unpublished_changes=True,
        )
        self.index.add_child(instance=article)
        revision = article.save_revision()

        with self.assertRaises(ValidationError):
            revision.publish()

        article.refresh_from_db()
        self.assertFalse(article.live)
        self.assertIn("an identified author", article.publication_errors())
        self.assertIn("at least one factual source", article.publication_errors())

    def test_source_and_review_metadata_are_required_for_publication(self):
        no_source = self.make_article("No source test", with_source=False)
        awaiting_review = self.make_article("Awaiting review test", reviewed=False)

        with self.assertRaises(ValidationError):
            no_source.get_latest_revision().publish()
        with self.assertRaises(ValidationError):
            awaiting_review.get_latest_revision().publish()

        self.assertFalse(BlogPage.objects.get(pk=no_source.pk).live)
        self.assertFalse(BlogPage.objects.get(pk=awaiting_review.pk).live)

    def test_review_dates_and_self_relationship_are_validated(self):
        article = self.make_article("Validation test")
        article.reviewed_on = timezone.localdate() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            article.full_clean()

        relationship = BlogRelatedArticle(page=article, related_article=article)
        with self.assertRaises(ValidationError):
            relationship.full_clean()

    def test_reviewed_article_renders_attribution_sources_and_disclaimer(self):
        category = BlogCategory.objects.create(
            name="Test education", slug="test-education"
        )
        self.publish_index()
        article = self.publish_article(
            self.make_article("Reviewed educational test", category=category)
        )

        response = self.client.get("/blog/reviewed-educational-test/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reviewed test content")
        self.assertContains(response, "Test Author")
        self.assertContains(response, "Test Reviewer")
        self.assertContains(response, "Test medical source")
        self.assertContains(response, "Test education")
        self.assertContains(response, "general educational purposes")
        self.assertIsNotNone(article.first_published_at)

        home_response = self.client.get("/")
        self.assertContains(home_response, "Reviewed educational test")

    def test_featured_image_uses_alt_text_and_wagtail_rendition(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            image_bytes = BytesIO()
            PillowImage.new("RGB", (1600, 900), color="#dfe7e4").save(
                image_bytes, format="JPEG"
            )
            image_bytes.seek(0)
            image = get_image_model().objects.create(
                title="Automated-test article image",
                file=ImageFile(image_bytes, name="test-article.jpg"),
            )
            self.publish_index()
            article = self.make_article("Image rendition test")
            article.featured_image = image
            article.featured_image_alt_text = "A neutral automated-test illustration"
            self.publish_article(article)

            response = self.client.get("/blog/image-rendition-test/")
            rendition = image.get_rendition("fill-1200x675")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'alt="A neutral automated-test illustration"')
            self.assertEqual((rendition.width, rendition.height), (1200, 675))

    def test_only_live_related_content_is_rendered(self):
        self.publish_index()
        main = self.make_article("Main related-content test")
        draft_related = self.make_article("Hidden related article")
        BlogRelatedArticle.objects.create(
            page=main,
            related_article=draft_related,
        )

        treatment_index = TreatmentIndexPage.objects.get()
        draft_treatment = TreatmentPage(
            title="Hidden related treatment",
            slug="hidden-related-treatment",
            summary="Automated-test treatment summary.",
            live=False,
            has_unpublished_changes=True,
        )
        treatment_index.add_child(instance=draft_treatment)
        draft_treatment.save_revision()
        main.related_treatments.add(draft_treatment)
        self.publish_article(main)

        response = self.client.get("/blog/main-related-content-test/")

        self.assertNotContains(response, 'href="/blog/hidden-related-article/"')
        self.assertNotContains(
            response,
            'href="/treatments/hidden-related-treatment/"',
        )

        self.publish_article(draft_related)
        treatment_index.save_revision().publish()
        draft_treatment.save_revision().publish()
        response = self.client.get("/blog/main-related-content-test/")
        self.assertContains(response, 'href="/blog/hidden-related-article/"')
        self.assertContains(
            response,
            'href="/treatments/hidden-related-treatment/"',
        )

    def test_index_category_filter_and_pagination_use_only_public_articles(self):
        category_a = BlogCategory.objects.create(name="Category A", slug="category-a")
        category_b = BlogCategory.objects.create(name="Category B", slug="category-b")
        self.index.posts_per_page = 3
        self.publish_index()
        for number in range(1, 5):
            self.publish_article(
                self.make_article(
                    f"Published article {number}",
                    category=category_a if number < 4 else category_b,
                )
            )
        self.make_article("Unpublished article", category=category_a)

        first_page = self.client.get("/blog/")
        second_page = self.client.get("/blog/?page=2")
        filtered = self.client.get("/blog/?category=category-b")

        self.assertContains(first_page, "Page 1 of 2")
        self.assertContains(second_page, "Published article 1")
        self.assertNotContains(first_page, "Unpublished article")
        self.assertContains(filtered, "Published article 4")
        self.assertNotContains(filtered, "Published article 3")
