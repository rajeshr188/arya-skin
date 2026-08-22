from django.test import TestCase, override_settings

from clinics.models import ClinicIndexPage, ClinicPage
from doctors.models import DoctorPage
from website.models import HomePage

from .models import TreatmentCategory, TreatmentFAQ, TreatmentIndexPage, TreatmentPage


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class TreatmentPageTests(TestCase):
    def test_empty_treatment_index_is_seeded_as_a_draft(self):
        treatment_index = TreatmentIndexPage.objects.get()

        self.assertFalse(treatment_index.live)
        self.assertEqual(treatment_index.slug, "treatments")
        self.assertEqual(treatment_index.get_parent().specific, HomePage.objects.get())
        self.assertEqual(TreatmentPage.objects.count(), 0)
        self.assertEqual(TreatmentCategory.objects.count(), 0)
        self.assertEqual(self.client.get("/treatments/").status_code, 404)

    def test_published_treatment_renders_structured_approved_content(self):
        doctor = DoctorPage.objects.get()
        clinic_index = ClinicIndexPage.objects.get()
        clinic = ClinicPage.objects.get(slug="sitapura")
        treatment_index = TreatmentIndexPage.objects.get()
        doctor.save_revision().publish()
        clinic_index.save_revision().publish()
        clinic.save_revision().publish()
        treatment_index.save_revision().publish()

        category = TreatmentCategory.objects.create(
            name="Sample category", slug="sample-category"
        )
        treatment = TreatmentPage(
            title="Sample patient information",
            slug="sample-patient-information",
            category=category,
            doctor=doctor,
            summary="A sample summary used only by the automated test.",
            overview="<p>Reviewed overview content.</p>",
            when_to_consult="<p>Reviewed consultation guidance.</p>",
            feature_on_homepage=True,
        )
        treatment_index.add_child(instance=treatment)
        treatment.available_at_clinics.add(clinic)
        TreatmentFAQ.objects.create(
            page=treatment,
            question="Sample question?",
            answer="<p>Sample reviewed answer.</p>",
        )
        treatment.save_revision().publish()

        response = self.client.get(
            "/treatments/sample-patient-information/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reviewed overview content")
        self.assertContains(response, "Reviewed consultation guidance")
        self.assertContains(response, "Sample question?")
        self.assertContains(response, "Dr. Naresh Rathod")
        self.assertContains(response, "Dolphin Derma Care")
        self.assertContains(response, "general educational purposes")

        home_response = self.client.get("/")
        self.assertContains(home_response, "Sample patient information")

    def test_draft_relationships_are_not_linked_from_a_live_treatment(self):
        treatment_index = TreatmentIndexPage.objects.get()
        treatment_index.save_revision().publish()
        treatment = TreatmentPage(
            title="Relationship visibility sample",
            slug="relationship-visibility-sample",
            doctor=DoctorPage.objects.get(),
            summary="A sample summary used only by the automated test.",
        )
        treatment_index.add_child(instance=treatment)
        treatment.available_at_clinics.add(ClinicPage.objects.get(slug="sitapura"))
        treatment.save_revision().publish()

        response = self.client.get(
            "/treatments/relationship-visibility-sample/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/clinics/sitapura/"')
        self.assertNotContains(response, 'href="/dr-naresh-rathod/"')
