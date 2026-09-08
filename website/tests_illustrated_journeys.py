from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from .models import (
    HomePage,
    IllustratedCareJourneyItem,
    IllustratedCareJourneyPage,
)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class IllustratedCareJourneyTests(TestCase):
    def setUp(self):
        self.page = IllustratedCareJourneyPage.objects.get()

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

    def test_page_is_seeded_as_a_menu_ready_empty_draft(self):
        self.assertFalse(self.page.live)
        self.assertTrue(self.page.show_in_menus)
        self.assertEqual(self.page.slug, "illustrated-care-journeys")
        self.assertEqual(self.page.get_parent().specific, HomePage.objects.get())
        self.assertEqual(self.page.journeys.count(), 0)
        self.assertEqual(
            self.client.get("/illustrated-care-journeys/").status_code,
            404,
        )
        self.assertNotContains(self.client.get("/"), "Illustrated care journeys")

    def test_importer_dry_run_does_not_change_content(self):
        output = StringIO()
        call_command("seed_illustrated_care_journeys", stdout=output)

        self.assertEqual(self.page.journeys.count(), 0)
        self.assertIn("would_create_illustrated_care_journeys=6", output.getvalue())
        self.assertIn("would_import_illustrations=12", output.getvalue())
        self.assertIn("doctor_review_required=true", output.getvalue())

    def test_importer_creates_unreviewed_draft_and_is_repeat_safe(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            output = StringIO()
            call_command(
                "seed_illustrated_care_journeys",
                execute=True,
                stdout=output,
            )
            self.page.refresh_from_db()
            journeys = list(self.page.journeys.order_by("sort_order"))

            self.assertEqual(len(journeys), 6)
            self.assertEqual(
                len(
                    {
                        image_id
                        for journey in journeys
                        for image_id in (
                            journey.before_image_id,
                            journey.after_image_id,
                        )
                    }
                ),
                12,
            )
            self.assertTrue(
                all(not item.illustration_disclosure_confirmed for item in journeys)
            )
            self.assertTrue(all(not item.presentation_reviewed for item in journeys))
            self.assertTrue(all(item.before_alt_text for item in journeys))
            self.assertTrue(all(item.after_alt_text for item in journeys))
            with self.assertRaises(ValidationError):
                self.page.save_revision().publish()

            rerun_output = StringIO()
            call_command(
                "seed_illustrated_care_journeys",
                execute=True,
                stdout=rerun_output,
            )

        self.page.refresh_from_db()
        self.assertFalse(self.page.live)
        self.assertEqual(self.page.journeys.count(), 6)
        self.assertIn("illustrated_care_journeys_created=6", output.getvalue())
        self.assertIn("illustrations_imported=12", output.getvalue())
        self.assertIn(
            "illustrated_care_journeys_unchanged=6",
            rerun_output.getvalue(),
        )

    def test_importer_adds_only_missing_suffix_and_preserves_existing_items(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            call_command("seed_illustrated_care_journeys", execute=True)
            journeys = list(self.page.journeys.order_by("sort_order"))
            first = journeys[0]
            first.caption = "Existing reviewed editorial caption"
            first.save(update_fields=("caption",))
            for journey in journeys[3:]:
                journey.delete()

            output = StringIO()
            call_command(
                "seed_illustrated_care_journeys",
                execute=True,
                stdout=output,
            )

        first.refresh_from_db()
        self.assertEqual(first.caption, "Existing reviewed editorial caption")
        self.assertEqual(self.page.journeys.count(), 6)
        self.assertIn("illustrated_care_journeys_created=3", output.getvalue())
        self.assertIn("illustrations_imported=6", output.getvalue())

    def test_importer_refuses_existing_editorial_content(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            before = self.make_image("existing-before", "#ddd0c8")
            after = self.make_image("existing-after", "#d5dfd0")
            IllustratedCareJourneyItem.objects.create(
                page=self.page,
                title="Existing editorial journey",
                before_image=before,
                after_image=after,
                before_alt_text="Existing first illustration",
                after_alt_text="Existing second illustration",
            )

            with self.assertRaises(CommandError):
                call_command("seed_illustrated_care_journeys", execute=True)

    def test_item_validation_requires_distinct_illustrations(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            image = self.make_image("same-illustration", "#dfe7e4")
            journey = IllustratedCareJourneyItem(
                page=self.page,
                title="Validation journey",
                before_image=image,
                after_image=image,
                before_alt_text="First validation illustration",
                after_alt_text="Second validation illustration",
            )

            with self.assertRaises(ValidationError) as error:
                journey.full_clean()

        self.assertIn("after_image", error.exception.message_dict)

    def test_reviewed_journeys_render_with_permanent_disclosure(self):
        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            call_command("seed_illustrated_care_journeys", execute=True)
            self.page.refresh_from_db()
            self.page.journeys.update(
                illustration_disclosure_confirmed=True,
                presentation_reviewed=True,
            )
            self.page.save_revision().publish()
            self.page.refresh_from_db()

            response = self.client.get("/illustrated-care-journeys/")
            homepage = self.client.get("/")

        self.assertTrue(self.page.live)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Illustrated change in visible acne")
        self.assertContains(response, "Illustrated before")
        self.assertContains(response, "Illustrated after")
        self.assertContains(response, "These are not patient photographs")
        self.assertContains(
            response,
            'alt="Illustration of an adult man with several raised acne blemishes',
        )
        self.assertContains(response, '"@type":"CollectionPage"')
        self.assertContains(homepage, 'href="/illustrated-care-journeys/"')
