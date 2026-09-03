from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
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

    def test_content_seed_is_dry_run_first_and_creates_only_reviewable_drafts(self):
        dry_run_output = StringIO()
        call_command("seed_treatment_drafts", stdout=dry_run_output)

        self.assertIn("would_create_treatment_drafts=5", dry_run_output.getvalue())
        self.assertEqual(TreatmentPage.objects.count(), 0)

        output = StringIO()
        call_command("seed_treatment_drafts", execute=True, stdout=output)

        treatment_index = TreatmentIndexPage.objects.get()
        treatments = TreatmentPage.objects.order_by("slug")
        self.assertFalse(treatment_index.live)
        self.assertIn("support an informed consultation", treatment_index.introduction)
        self.assertEqual(treatments.count(), 5)
        self.assertEqual(TreatmentCategory.objects.count(), 3)
        for treatment in treatments:
            with self.subTest(treatment=treatment.slug):
                self.assertFalse(treatment.live)
                self.assertFalse(treatment.show_in_menus)
                self.assertFalse(treatment.feature_on_homepage)
                self.assertEqual(treatment.doctor, DoctorPage.objects.get())
                self.assertEqual(treatment.available_at_clinics.count(), 2)
                self.assertEqual(treatment.faqs.count(), 3)
                self.assertTrue(treatment.summary)
                self.assertTrue(treatment.search_description)
                self.assertEqual(self.client.get(treatment.url).status_code, 404)
        self.assertIn("treatment_drafts_created=5", output.getvalue())
        self.assertIn("medical_review_required=true", output.getvalue())

        rerun_output = StringIO()
        call_command("seed_treatment_drafts", execute=True, stdout=rerun_output)
        self.assertIn("treatment_drafts_unchanged=5", rerun_output.getvalue())
        self.assertEqual(TreatmentPage.objects.count(), 5)

    def test_content_seed_refuses_a_partial_existing_set(self):
        index = TreatmentIndexPage.objects.get()
        index.add_child(
            instance=TreatmentPage(
                title="Existing acne page",
                slug="acne-assessment-treatment",
                summary="Existing editorial content must not be overwritten.",
                live=False,
            )
        )

        with self.assertRaisesMessage(CommandError, "partial seed"):
            call_command("seed_treatment_drafts", execute=True)

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
