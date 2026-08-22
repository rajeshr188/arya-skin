from django.test import TestCase, override_settings
from wagtail.blocks import StructBlockValidationError

from clinics.models import ClinicIndexPage, ClinicPage

from .blocks import CallToActionBlock, ContentStreamBlock
from .models import ContactPage, HomePage, StandardPage


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class Milestone2BWebsiteTests(TestCase):
    def test_empty_supporting_pages_are_seeded_as_drafts(self):
        self.assertEqual(ContactPage.objects.count(), 1)
        self.assertEqual(StandardPage.objects.count(), 2)
        self.assertFalse(ContactPage.objects.get().live)
        self.assertTrue(all(not page.live for page in StandardPage.objects.all()))

        for route in ("/contact/", "/privacy/", "/medical-disclaimer/"):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(route).status_code, 404)

    def test_contact_page_only_lists_published_clinics(self):
        contact = ContactPage.objects.get()
        clinic_index = ClinicIndexPage.objects.get()
        sitapura = ClinicPage.objects.get(slug="sitapura")
        contact.introduction = "<p>Select a clinic location.</p>"
        contact.save_revision().publish()
        clinic_index.save_revision().publish()
        sitapura.save_revision().publish()

        response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dolphin Derma Care")
        self.assertNotContains(response, 'href="/clinics/chaksu/"')
        self.assertNotContains(response, "9461289316")
        self.assertContains(self.client.get("/"), 'href="/contact/"')

    def test_standard_page_renders_constrained_stream_content(self):
        page = StandardPage.objects.get(slug="privacy")
        page.introduction = "<p>Test introduction.</p>"
        page.body = [("rich_text", "<p>Test body content.</p>")]
        page.save_revision().publish()

        response = self.client.get("/privacy/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test introduction")
        self.assertContains(response, "Test body content")

    def test_shared_stream_is_deliberately_constrained(self):
        self.assertEqual(
            list(ContentStreamBlock().child_blocks),
            [
                "heading",
                "rich_text",
                "image",
                "image_text",
                "quote",
                "faq",
                "call_to_action",
                "doctor_advice",
                "information",
            ],
        )

    def test_call_to_action_requires_exactly_one_destination(self):
        block = CallToActionBlock()

        with self.assertRaises(StructBlockValidationError):
            block.clean(
                block.to_python(
                    {
                        "heading": "Next step",
                        "text": "",
                        "label": "Continue",
                        "internal_page": None,
                        "external_url": "",
                    }
                )
            )

    def test_homepage_sections_are_driven_by_published_content(self):
        home = HomePage.objects.get()
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, home.hero_eyebrow)
        self.assertNotContains(response, "View professional profile")
        self.assertNotContains(response, "Contact a clinic")
