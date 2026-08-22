from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from appointments.models import AppointmentEnquiry


class Command(BaseCommand):
    help = "Delete closed appointment enquiries after the approved retention period."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=settings.APPOINTMENT_ENQUIRY_RETENTION_DAYS,
            help="Delete enquiries marked closed before this many days ago.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report the number eligible for deletion without deleting them.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days < 1:
            raise CommandError("--days must be at least 1.")

        cutoff = timezone.now() - timedelta(days=days)
        enquiries = AppointmentEnquiry.objects.filter(
            status=AppointmentEnquiry.Status.CLOSED,
            updated_at__lt=cutoff,
        )
        count = enquiries.count()

        if options["dry_run"]:
            self.stdout.write(f"eligible_closed_enquiries={count}")
            return

        enquiries.delete()
        self.stdout.write(f"deleted_closed_enquiries={count}")
