from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from blog.content_drafts import BLOG_DRAFTS
from blog.models import BlogAuthor, BlogPage
from doctors.models import DoctorPage


AUTHOR_NAME = "Dr. Naresh Rathod"
AUTHOR_ROLE = "Dermatologist and Cosmetologist"


class Command(BaseCommand):
    help = "Assign the owner-approved author and medical reviewer to blog drafts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Assign the roles. Without this flag, only report the plan.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        target_slugs = {draft["slug"] for draft in BLOG_DRAFTS}
        pages = {
            page.slug: page
            for page in BlogPage.objects.filter(slug__in=target_slugs)
        }
        if set(pages) != target_slugs:
            raise CommandError("All three prepared blog drafts are required.")

        doctor = DoctorPage.objects.get()
        people = list(BlogAuthor.objects.filter(name=AUTHOR_NAME))
        if len(people) > 1:
            raise CommandError(
                "Multiple blog-author records use Dr. Naresh Rathod's name; "
                "refusing an ambiguous assignment."
            )
        person = people[0] if people else None
        if person and (
            person.role != AUTHOR_ROLE or person.doctor_page_id != doctor.id
        ):
            raise CommandError(
                "The existing Dr. Naresh Rathod author record has unexpected details."
            )

        for page in pages.values():
            if page.author_id and (not person or page.author_id != person.id):
                raise CommandError(
                    f"Article {page.slug} already has a different author."
                )
            if page.reviewed_by_id and (
                not person or page.reviewed_by_id != person.id
            ):
                raise CommandError(
                    f"Article {page.slug} already has a different medical reviewer."
                )

        if person and all(
            page.author_id == person.id and page.reviewed_by_id == person.id
            for page in pages.values()
        ):
            self.stdout.write(f"blog_editorial_roles_unchanged={len(pages)}")
            return

        if not options["execute"]:
            self.stdout.write(f"would_assign_blog_editorial_roles={len(pages)}")
            self.stdout.write(f"author={AUTHOR_NAME}")
            self.stdout.write(f"role={AUTHOR_ROLE}")
            self.stdout.write("completed_medical_review=false")
            return

        if not person:
            person = BlogAuthor.objects.create(
                name=AUTHOR_NAME,
                role=AUTHOR_ROLE,
                doctor_page=doctor,
            )

        for page in pages.values():
            page.author = person
            page.reviewed_by = person
            page.save(update_fields=("author", "reviewed_by"))
            page.save_revision(log_action=True)

        self.stdout.write(f"blog_editorial_roles_assigned={len(pages)}")
        self.stdout.write(f"author={AUTHOR_NAME}")
        self.stdout.write(f"role={AUTHOR_ROLE}")
        self.stdout.write("completed_medical_review=false")
