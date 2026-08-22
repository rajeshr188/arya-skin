import json
import re
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from appointments.models import AppointmentEnquiry
from clinics.models import ClinicIndexPage, ClinicPage
from treatments.models import TreatmentIndexPage, TreatmentPage
from website.models import SiteSettings, StandardPage


def analytics_config(response):
    match = re.search(
        rb'<script id="analytics-config" type="application/json">(.*?)</script>',
        response.content,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError("No analytics configuration found")
    return json.loads(match.group(1))


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class PrivacySafeAnalyticsTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.site_settings = SiteSettings.for_site(self.site)
        self.clinic_index = ClinicIndexPage.objects.get()
        self.sitapura = ClinicPage.objects.get(slug="sitapura")

    def enable_ga4(self):
        self.publish_privacy_notice()
        self.site_settings.analytics_enabled = True
        self.site_settings.google_analytics_id = "G-TEST123456"
        self.site_settings.google_tag_manager_id = ""
        self.site_settings.save()

    def publish_privacy_notice(self):
        privacy_page = StandardPage.objects.get(slug="privacy")
        privacy_page.save_revision().publish()

    def publish_clinic(self):
        if not self.clinic_index.live:
            self.clinic_index.save_revision().publish()
        self.sitapura.save_revision().publish()
        self.sitapura.refresh_from_db()

    def test_analytics_is_absent_until_explicitly_enabled(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="analytics-config"')
        self.assertNotContains(response, 'id="analytics-consent"')
        self.assertNotContains(response, "googletagmanager.com")
        self.assertContains(response, 'data-analytics-page-type="home"')

    def test_settings_require_one_well_formed_provider_id(self):
        self.site_settings.analytics_enabled = True
        with self.assertRaises(ValidationError):
            self.site_settings.full_clean()

        self.site_settings.google_analytics_id = "UA-OLD-FORMAT"
        with self.assertRaises(ValidationError):
            self.site_settings.full_clean()

        self.site_settings.google_analytics_id = "G-TEST123456"
        self.site_settings.google_tag_manager_id = "GTM-TEST123"
        with self.assertRaises(ValidationError):
            self.site_settings.full_clean()

        self.site_settings.google_tag_manager_id = ""
        self.site_settings.full_clean()

    def test_ga4_configuration_is_rendered_without_loading_google_in_html(self):
        self.enable_ga4()

        response = self.client.get("/")

        self.assertEqual(
            analytics_config(response),
            {"provider": "ga4", "tracking_id": "G-TEST123456"},
        )
        self.assertContains(response, 'id="analytics-consent"')
        self.assertContains(response, 'data-analytics-consent="accept"')
        self.assertContains(response, 'data-analytics-consent="decline"')
        self.assertNotContains(response, "googletagmanager.com")

    def test_enabled_id_still_requires_a_published_privacy_notice(self):
        self.site_settings.analytics_enabled = True
        self.site_settings.google_analytics_id = "G-TEST123456"
        self.site_settings.save()

        response = self.client.get("/")

        self.assertNotContains(response, 'id="analytics-config"')
        self.assertNotContains(response, 'id="analytics-consent"')

    def test_tag_manager_and_search_console_configuration_are_supported(self):
        self.publish_privacy_notice()
        self.site_settings.analytics_enabled = True
        self.site_settings.google_tag_manager_id = "gtm-test123"
        self.site_settings.google_search_console_verification = "verify_token-123"
        self.site_settings.save()

        response = self.client.get("/")

        self.assertEqual(
            analytics_config(response),
            {"provider": "gtm", "tracking_id": "GTM-TEST123"},
        )
        self.assertContains(
            response,
            '<meta name="google-site-verification" content="verify_token-123">',
        )

    def test_clinic_actions_and_view_use_only_safe_stable_identifiers(self):
        self.enable_ga4()
        self.sitapura.phone_is_public = True
        self.sitapura.whatsapp = "+919999999999"
        self.sitapura.whatsapp_is_public = True
        self.sitapura.google_maps_url = "https://maps.example.test/sitapura"
        self.publish_clinic()

        response = self.client.get("/clinics/sitapura/")

        self.assertContains(response, 'data-analytics-page-type="clinic"')
        self.assertContains(response, 'data-analytics-event-on-load="clinic_view"')
        self.assertContains(response, 'data-analytics-clinic="sitapura"')
        self.assertContains(
            response,
            'data-analytics-event="appointment_click" '
            'data-analytics-clinic="sitapura"',
            count=2,
        )
        for event_name in ("phone_click", "whatsapp_click", "directions_click"):
            self.assertContains(
                response,
                f'data-analytics-event="{event_name}"',
                count=2,
            )
        self.assertNotContains(response, "data-analytics-phone")
        self.assertNotContains(response, "data-analytics-whatsapp")

    def test_treatment_page_has_view_and_clinic_appointment_events(self):
        self.enable_ga4()
        self.publish_clinic()
        treatment_index = TreatmentIndexPage.objects.get()
        treatment_index.save_revision().publish()
        treatment = TreatmentPage(
            title="Analytics test treatment",
            slug="analytics-test-treatment",
            summary="Automated test summary.",
        )
        treatment_index.add_child(instance=treatment)
        treatment.available_at_clinics.add(self.sitapura)
        treatment.save_revision().publish()

        response = self.client.get("/treatments/analytics-test-treatment/")

        self.assertContains(response, 'data-analytics-page-type="treatment"')
        self.assertContains(
            response,
            'data-analytics-event-on-load="treatment_view"',
        )
        self.assertContains(
            response,
            'data-analytics-treatment="analytics-test-treatment"',
        )
        self.assertContains(response, 'data-analytics-event="appointment_click"')
        self.assertContains(response, 'data-analytics-clinic="sitapura"')

    def test_accepted_appointment_event_is_one_time_and_contains_no_form_data(self):
        self.enable_ga4()
        self.publish_clinic()
        form_response = self.client.get(
            reverse(
                "appointments:request_for_clinic",
                kwargs={"clinic_slug": "sitapura"},
            )
        )
        payload = {
            "clinic": self.sitapura.pk,
            "name": "Analytics Test Patient",
            "phone": "+91 98765 43210",
            "email": "analytics-patient@example.com",
            "preferred_date": (
                timezone.localdate() + timedelta(days=3)
            ).isoformat(),
            "time_preference": AppointmentEnquiry.TimePreference.MORNING,
            "consent_to_contact": "on",
            "form_token": form_response.context["form"].initial["form_token"],
            "website": "",
        }

        response = self.client.post(form_response.request["PATH_INFO"], payload)
        success = self.client.get(response.url)

        self.assertContains(
            success,
            'data-analytics-event-on-load="appointment_form_submit"',
        )
        self.assertContains(success, 'data-analytics-success="accepted"')
        self.assertContains(success, 'data-analytics-clinic="sitapura"')
        self.assertNotContains(success, "Analytics Test Patient")
        self.assertNotContains(success, "analytics-patient@example.com")
        self.assertRedirects(self.client.get(response.url), "/")

    def test_client_script_uses_basic_consent_and_a_fixed_event_allowlist(self):
        script_path = Path(finders.find("js/base.js"))
        script = script_path.read_text(encoding="utf-8")

        self.assertLess(
            script.index('gtag("consent", "default"'),
            script.index('"https://www.googletagmanager.com/gtag/js?id="'),
        )
        for event_name in (
            "phone_click",
            "whatsapp_click",
            "directions_click",
            "appointment_click",
            "appointment_form_submit",
            "clinic_view",
            "treatment_view",
        ):
            self.assertIn(f'"{event_name}"', script)
        self.assertNotIn("FormData", script)
        self.assertNotIn("medical_concern", script)
        self.assertNotIn("data-analytics-phone", script)
