from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from doctors.models import DoctorPage

from .models import ClinicIndexPage, ClinicPage


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class ClinicPageTests(TestCase):
    def test_two_supplied_clinics_are_seeded_as_drafts(self):
        clinic_index = ClinicIndexPage.objects.get()
        clinics = ClinicPage.objects.order_by("path")

        self.assertFalse(clinic_index.live)
        self.assertEqual(clinics.count(), 2)
        self.assertEqual(
            list(clinics.values_list("title", "slug", "locality")),
            [
                ("Dolphin Derma Care", "sitapura", "Sitapura"),
                ("Arya Skin and Hair Clinic", "chaksu", "Chaksu"),
            ],
        )
        self.assertTrue(all(not clinic.live for clinic in clinics))
        self.assertTrue(all(clinic.doctor_id for clinic in clinics))

    def test_draft_clinic_routes_are_not_public(self):
        self.assertEqual(self.client.get("/clinics/").status_code, 404)
        self.assertEqual(self.client.get("/clinics/sitapura/").status_code, 404)
        self.assertEqual(self.client.get("/clinics/chaksu/").status_code, 404)

    def test_seeded_contact_data_requires_publication_consent(self):
        clinic = ClinicPage.objects.get(slug="sitapura")

        self.assertEqual(clinic.phone, "9461289316")
        self.assertEqual(clinic.whatsapp, "9461289316")
        self.assertFalse(clinic.phone_is_public)
        self.assertFalse(clinic.whatsapp_is_public)
        self.assertEqual(clinic.phone_uri, "")
        self.assertEqual(clinic.whatsapp_url, "")

    def test_contact_visibility_switches_control_rendered_actions(self):
        doctor = DoctorPage.objects.get()
        clinic_index = ClinicIndexPage.objects.get()
        clinic = ClinicPage.objects.get(slug="sitapura")
        doctor.save_revision().publish()
        clinic_index.save_revision().publish()
        clinic.save_revision().publish()

        private_response = self.client.get("/clinics/sitapura/")
        self.assertEqual(private_response.status_code, 200)
        self.assertNotContains(private_response, "Call clinic")
        self.assertNotContains(private_response, "wa.me")

        clinic.phone_is_public = True
        clinic.whatsapp = "+919461289316"
        clinic.whatsapp_is_public = True
        clinic.save_revision().publish()

        public_response = self.client.get("/clinics/sitapura/")
        self.assertContains(public_response, 'href="tel:9461289316"')
        self.assertContains(public_response, "https://wa.me/919461289316")
        self.assertNotContains(public_response, "general_concern")

    def test_public_contact_switch_requires_a_number(self):
        clinic = ClinicPage.objects.get(slug="sitapura")
        clinic.phone = ""
        clinic.phone_is_public = True

        with self.assertRaises(ValidationError):
            clinic.full_clean()

    def test_public_whatsapp_requires_international_format(self):
        clinic = ClinicPage.objects.get(slug="sitapura")
        clinic.whatsapp_is_public = True

        with self.assertRaises(ValidationError):
            clinic.full_clean()
