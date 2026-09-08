from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.images import get_image_model

from website.illustrated_care_journey_drafts import (
    ILLUSTRATED_CARE_JOURNEY_INTRODUCTION,
    ILLUSTRATED_CARE_JOURNEYS,
)
from website.models import IllustratedCareJourneyItem, IllustratedCareJourneyPage


ASSET_DIRECTORY = (
    Path(__file__).resolve().parents[3] / "content_assets" / "before_after"
)


class Command(BaseCommand):
    help = "Import the prepared illustrated care journeys as an unpublished draft."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Create the draft content. Without this flag, only report the plan.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        page = IllustratedCareJourneyPage.objects.select_for_update().get()
        expected_titles = [journey["title"] for journey in ILLUSTRATED_CARE_JOURNEYS]
        existing_titles = list(
            page.journeys.order_by("sort_order", "id").values_list(
                "title", flat=True
            )
        )

        if existing_titles == expected_titles:
            self.stdout.write(
                f"illustrated_care_journeys_unchanged={len(existing_titles)}"
            )
            return
        if existing_titles != expected_titles[: len(existing_titles)]:
            raise CommandError(
                "The illustrated care journeys page already has editorial content; "
                "refusing to overwrite it."
            )

        if page.live:
            raise CommandError(
                "The illustrated care journeys page is already published; refusing "
                "to seed it."
            )
        if (
            page.introduction
            and str(page.introduction) != ILLUSTRATED_CARE_JOURNEY_INTRODUCTION
        ):
            raise CommandError(
                "The illustrated care journeys introduction has editorial content; "
                "refusing to overwrite it."
            )

        missing_journeys = ILLUSTRATED_CARE_JOURNEYS[len(existing_titles) :]
        filenames = [
            image_details["filename"]
            for journey in missing_journeys
            for image_details in (journey["before"], journey["after"])
        ]
        missing_assets = [
            filename
            for filename in filenames
            if not (ASSET_DIRECTORY / filename).is_file()
        ]
        if missing_assets:
            raise CommandError(
                "Missing required illustrated care journey assets: "
                + ", ".join(sorted(missing_assets))
            )

        if not options["execute"]:
            self.stdout.write(
                f"would_create_illustrated_care_journeys={len(missing_journeys)}"
            )
            self.stdout.write(f"would_import_illustrations={len(filenames)}")
            self.stdout.write("illustrated_care_journey_page_published=false")
            self.stdout.write("doctor_review_required=true")
            return

        page.introduction = ILLUSTRATED_CARE_JOURNEY_INTRODUCTION
        page.save(update_fields=("introduction",))

        Image = get_image_model()
        for sort_order, journey in enumerate(
            missing_journeys,
            start=len(existing_titles),
        ):
            imported_images = {}
            for position in ("before", "after"):
                image_details = journey[position]
                image_path = ASSET_DIRECTORY / image_details["filename"]
                with image_path.open("rb") as image_file:
                    image = Image(
                        title=image_details["title"],
                        description=image_details["alt_text"],
                    )
                    image.file.save(
                        image_details["filename"],
                        File(image_file),
                        save=True,
                    )
                imported_images[position] = image

            IllustratedCareJourneyItem.objects.create(
                page=page,
                sort_order=sort_order,
                title=journey["title"],
                before_image=imported_images["before"],
                after_image=imported_images["after"],
                before_alt_text=journey["before"]["alt_text"],
                after_alt_text=journey["after"]["alt_text"],
                caption=journey["caption"],
                illustration_disclosure_confirmed=False,
                presentation_reviewed=False,
            )

        page.save_revision(log_action=True)
        self.stdout.write(
            f"illustrated_care_journeys_created={len(missing_journeys)}"
        )
        self.stdout.write(f"illustrations_imported={len(filenames)}")
        self.stdout.write("illustrated_care_journey_page_published=false")
        self.stdout.write("doctor_review_required=true")
