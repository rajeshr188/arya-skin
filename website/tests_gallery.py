from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.test import TestCase, override_settings
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from .models import (
    BeforeAfterGalleryItem,
    BeforeAfterGalleryPage,
    HomePage,
)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class BeforeAfterGalleryTests(TestCase):
    def setUp(self):
        self.gallery = BeforeAfterGalleryPage.objects.get()

    def make_image(self, name, color):
        image_bytes = BytesIO()
        PillowImage.new("RGB", (800, 600), color=color).save(
            image_bytes,
            format="JPEG",
        )
        image_bytes.seek(0)
        return get_image_model().objects.create(
            title=f"Automated test {name}",
            file=ImageFile(image_bytes, name=f"{name}.jpg"),
        )

    def test_empty_gallery_is_seeded_as_a_menu_ready_draft(self):
        self.assertFalse(self.gallery.live)
        self.assertTrue(self.gallery.show_in_menus)
        self.assertEqual(self.gallery.slug, "before-after")
        self.assertEqual(self.gallery.get_parent().specific, HomePage.objects.get())
        self.assertEqual(self.gallery.comparisons.count(), 0)
        self.assertEqual(self.client.get("/before-after/").status_code, 404)
        self.assertNotContains(self.client.get("/"), "Before and after")

    def test_empty_or_unapproved_gallery_cannot_be_published(self):
        empty_revision = self.gallery.save_revision()
        with self.assertRaises(ValidationError):
            empty_revision.publish()

        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            before = self.make_image("unapproved-before", "#ddd0c8")
            after = self.make_image("unapproved-after", "#d5dfd0")
            BeforeAfterGalleryItem.objects.create(
                page=self.gallery,
                title="Unapproved automated comparison",
                before_image=before,
                after_image=after,
                before_alt_text="Before view used in an automated test",
                after_alt_text="After view used in an automated test",
                publication_consent_confirmed=False,
                presentation_reviewed=True,
            )
            revision = self.gallery.save_revision()

            with self.assertRaises(ValidationError):
                revision.publish()

        self.gallery.refresh_from_db()
        self.assertFalse(self.gallery.live)

    def test_comparison_validation_requires_distinct_images_and_approvals(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            image = self.make_image("validation", "#dfe7e4")
            comparison = BeforeAfterGalleryItem(
                page=self.gallery,
                title="Validation comparison",
                before_image=image,
                after_image=image,
                before_alt_text="Before validation view",
                after_alt_text="After validation view",
            )

            with self.assertRaises(ValidationError):
                comparison.full_clean()

            comparison.publication_consent_confirmed = True
            comparison.presentation_reviewed = True
            with self.assertRaises(ValidationError) as error:
                comparison.full_clean()

        self.assertIn("after_image", error.exception.message_dict)

    def test_approved_gallery_renders_labels_descriptions_and_notice(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            before = self.make_image("approved-before", "#e4d3c8")
            after = self.make_image("approved-after", "#d3e1d0")
            BeforeAfterGalleryItem.objects.create(
                page=self.gallery,
                title="Neutral automated comparison",
                before_image=before,
                after_image=after,
                before_alt_text="Visible area before the automated comparison",
                after_alt_text="Visible area after the automated comparison",
                caption="Verified neutral context for an automated test.",
                publication_consent_confirmed=True,
                presentation_reviewed=True,
            )
            self.gallery.save_revision().publish()

            self.gallery.refresh_from_db()
            self.assertTrue(self.gallery.live)
            self.assertTrue(self.gallery.show_in_menus)
            menu_page_ids = (
                HomePage.objects.get()
                .get_children()
                .live()
                .public()
                .in_menu()
                .values_list("id", flat=True)
            )
            self.assertIn(self.gallery.id, menu_page_ids)

            response = self.client.get("/before-after/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Neutral automated comparison")
        self.assertContains(response, ">Before<")
        self.assertContains(response, ">After<")
        self.assertContains(
            response,
            'alt="Visible area before the automated comparison"',
        )
        self.assertContains(
            response,
            'alt="Visible area after the automated comparison"',
        )
        self.assertContains(response, "Results vary from person to person")
        self.assertContains(response, '"@type":"CollectionPage"')
        self.assertContains(self.client.get("/"), 'href="/before-after/"')
