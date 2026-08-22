from django.test import TestCase, override_settings

from website.models import HomePage

from .models import DoctorPage


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class DoctorPageTests(TestCase):
    def test_seeded_doctor_is_structured_and_draft(self):
        doctor = DoctorPage.objects.get()

        self.assertFalse(doctor.live)
        self.assertEqual(doctor.get_parent().specific, HomePage.objects.get())
        self.assertEqual(doctor.slug, "dr-naresh-rathod")
        self.assertEqual(doctor.qualifications.count(), 2)
        self.assertEqual(doctor.registrations.get().registration_number, "C-6523")
        self.assertEqual(
            list(doctor.languages.values_list("name", flat=True)),
            ["Hindi", "English", "Marwari"],
        )
        self.assertIsNone(doctor.experience_years)
        self.assertIsNone(doctor.experience_as_of_date)

    def test_draft_doctor_is_not_public(self):
        response = self.client.get("/dr-naresh-rathod/")

        self.assertEqual(response.status_code, 404)

    def test_published_doctor_template_renders_structured_credentials(self):
        doctor = DoctorPage.objects.get()
        doctor.save_revision().publish()

        response = self.client.get("/dr-naresh-rathod/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dermatologist and Cosmetologist")
        self.assertContains(response, "Jhalawar Medical College")
        self.assertContains(response, "Rajasthan Medical Council")
