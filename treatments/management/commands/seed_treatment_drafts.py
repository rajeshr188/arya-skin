from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clinics.models import ClinicPage
from doctors.models import DoctorPage
from treatments.content_drafts import (
    TREATMENT_DRAFTS,
    TREATMENT_INDEX_INTRODUCTION,
)
from treatments.models import (
    TreatmentCategory,
    TreatmentFAQ,
    TreatmentIndexPage,
    TreatmentPage,
)


class Command(BaseCommand):
    help = "Create reviewed-source treatment content as unpublished Wagtail drafts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Create the drafts. Without this flag, only report the plan.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        target_slugs = {draft["slug"] for draft in TREATMENT_DRAFTS}
        existing_slugs = set(
            TreatmentPage.objects.filter(slug__in=target_slugs).values_list(
                "slug", flat=True
            )
        )
        if existing_slugs == target_slugs:
            self.stdout.write(f"treatment_drafts_unchanged={len(existing_slugs)}")
            return
        if existing_slugs:
            raise CommandError(
                "Some target treatment slugs already exist; refusing a partial seed."
            )
        if not options["execute"]:
            self.stdout.write(f"would_create_treatment_drafts={len(target_slugs)}")
            return

        index = TreatmentIndexPage.objects.select_for_update().get()
        if index.live:
            raise CommandError(
                "The Treatments index is already live; create and review drafts manually."
            )
        if index.introduction and str(index.introduction) != TREATMENT_INDEX_INTRODUCTION:
            raise CommandError(
                "The Treatments index has editorial content; refusing to overwrite it."
            )

        doctor = DoctorPage.objects.get()
        clinics = list(ClinicPage.objects.filter(slug__in=("sitapura", "chaksu")))
        if len(clinics) != 2:
            raise CommandError("Both approved clinic pages are required.")

        index.introduction = TREATMENT_INDEX_INTRODUCTION
        index.save(update_fields=("introduction",))
        index.save_revision(log_action=True)

        created = 0
        for draft in TREATMENT_DRAFTS:
            category_name, category_slug = draft["category"]
            category, _ = TreatmentCategory.objects.get_or_create(
                slug=category_slug,
                defaults={"name": category_name},
            )
            if category.name != category_name:
                raise CommandError(
                    f"Category slug {category_slug} has an unexpected name."
                )

            page = TreatmentPage(
                title=draft["title"],
                slug=draft["slug"],
                category=category,
                doctor=doctor,
                summary=draft["summary"],
                search_description=draft["search_description"],
                overview=draft.get("overview", ""),
                symptoms=draft.get("symptoms", ""),
                common_causes=draft.get("common_causes", ""),
                diagnosis=draft.get("diagnosis", ""),
                when_to_consult=draft.get("when_to_consult", ""),
                treatment_approaches=draft.get("treatment_approaches", ""),
                what_to_expect=draft.get("what_to_expect", ""),
                feature_on_homepage=False,
                show_in_menus=False,
                live=False,
                has_unpublished_changes=True,
            )
            index.add_child(instance=page)
            page.available_at_clinics.add(*clinics)
            for question, answer in draft["faqs"]:
                TreatmentFAQ.objects.create(
                    page=page,
                    question=question,
                    answer=answer,
                )
            page.save()
            page.save_revision(log_action=True)
            created += 1

        self.stdout.write(f"treatment_drafts_created={created}")
        self.stdout.write("treatment_index_published=false")
        self.stdout.write("medical_review_required=true")
