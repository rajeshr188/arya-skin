from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import Site

from .models import HomePage, SiteSettings


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class WagtailFoundationTests(TestCase):
    def test_seeded_homepage_is_live_and_served(self):
        home = HomePage.objects.get()

        self.assertTrue(home.live)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Naresh Rathod")
        self.assertContains(response, "Dolphin Derma Care")
        self.assertContains(response, "Arya Skin and Hair Clinic")

    def test_site_settings_contain_only_known_identity_facts(self):
        site = Site.objects.get(is_default_site=True)
        settings = SiteSettings.for_site(site)

        self.assertEqual(settings.site_title, "Dr. Naresh Rathod - Dermatologist")
        self.assertEqual(settings.professional_title, "Dermatologist and Cosmetologist")
        self.assertEqual(settings.primary_phone, "")
        self.assertEqual(settings.default_whatsapp, "")

    def test_wagtail_admin_login_is_available(self):
        response = self.client.get(reverse("wagtailadmin_login"))

        self.assertEqual(response.status_code, 200)

    def test_public_allauth_routes_are_not_exposed(self):
        response = self.client.get("/accounts/signup/")

        self.assertEqual(response.status_code, 404)

    def test_sitemap_lists_the_homepage(self):
        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "http://localhost/")
