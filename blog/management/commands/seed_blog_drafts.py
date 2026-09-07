from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.images import get_image_model

from blog.content_drafts import (
    BLOG_DRAFTS,
    BLOG_INDEX_INTRODUCTION,
    SOURCE_ACCESSED_ON,
)
from blog.models import BlogCategory, BlogIndexPage, BlogPage, BlogSource
from treatments.models import TreatmentPage


ASSET_DIRECTORY = Path(__file__).resolve().parents[3] / "content_assets" / "blog"


class Command(BaseCommand):
    help = "Create missing source-checked articles as illustrated unpublished drafts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Create the drafts. Without this flag, only report the plan.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        target_slugs = {draft["slug"] for draft in BLOG_DRAFTS}
        existing_pages = list(BlogPage.objects.filter(slug__in=target_slugs))
        existing_slugs = {page.slug for page in existing_pages}
        missing_drafts = [
            draft for draft in BLOG_DRAFTS if draft["slug"] not in existing_slugs
        ]
        if existing_slugs == target_slugs:
            self.stdout.write(f"blog_drafts_unchanged={len(existing_slugs)}")
            return

        missing_assets = [
            draft["image"]["filename"]
            for draft in missing_drafts
            if not (ASSET_DIRECTORY / draft["image"]["filename"]).is_file()
        ]
        if missing_assets:
            raise CommandError(
                "Missing required blog illustration assets: "
                + ", ".join(sorted(missing_assets))
            )

        treatment_slugs = {
            draft["related_treatment_slug"] for draft in missing_drafts
        }
        treatments = {
            page.slug: page
            for page in TreatmentPage.objects.filter(slug__in=treatment_slugs)
        }
        if set(treatments) != treatment_slugs:
            raise CommandError("All related treatment drafts are required.")

        index = BlogIndexPage.objects.select_for_update().get()
        if any(page.get_parent().pk != index.pk for page in existing_pages):
            raise CommandError(
                "A prepared article slug exists outside the Articles index."
            )
        if (
            not existing_pages
            and index.introduction
            and str(index.introduction) != BLOG_INDEX_INTRODUCTION
        ):
            raise CommandError(
                "The Articles index has editorial content; refusing to overwrite it."
            )

        if not options["execute"]:
            self.stdout.write(f"would_create_blog_drafts={len(missing_drafts)}")
            self.stdout.write(
                f"would_import_blog_illustrations={len(missing_drafts)}"
            )
            self.stdout.write(f"existing_blog_drafts_preserved={len(existing_slugs)}")
            self.stdout.write(
                f"blog_index_published={str(index.live).lower()}"
            )
            self.stdout.write("author_and_medical_review_required=true")
            return

        if not index.live and not index.introduction:
            index.introduction = BLOG_INDEX_INTRODUCTION
            index.save(update_fields=("introduction",))
            index.save_revision(log_action=True)

        Image = get_image_model()
        created = 0
        for draft in missing_drafts:
            category_name, category_slug = draft["category"]
            category, _ = BlogCategory.objects.get_or_create(
                slug=category_slug,
                defaults={"name": category_name},
            )
            if category.name != category_name:
                raise CommandError(
                    f"Category slug {category_slug} has an unexpected name."
                )

            image_details = draft["image"]
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

            page = BlogPage(
                title=draft["title"],
                slug=draft["slug"],
                excerpt=draft["excerpt"],
                search_description=draft["search_description"],
                featured_image=image,
                featured_image_alt_text=image_details["alt_text"],
                body=draft["body"],
                review_status=BlogPage.ReviewStatus.AWAITING_REVIEW,
                show_in_menus=False,
                live=False,
                has_unpublished_changes=True,
            )
            index.add_child(instance=page)
            page.categories.add(category)
            page.related_treatments.add(treatments[draft["related_treatment_slug"]])
            for source in draft["sources"]:
                BlogSource.objects.create(
                    page=page,
                    title=source["title"],
                    publisher=source["publisher"],
                    url=source["url"],
                    accessed_on=draft.get(
                        "source_accessed_on", SOURCE_ACCESSED_ON
                    ),
                )
            page.save()
            page.save_revision(log_action=True)
            created += 1

        self.stdout.write(f"blog_drafts_created={created}")
        self.stdout.write(f"blog_illustrations_imported={created}")
        self.stdout.write(f"existing_blog_drafts_preserved={len(existing_slugs)}")
        self.stdout.write(f"blog_index_published={str(index.live).lower()}")
        self.stdout.write("author_and_medical_review_required=true")
