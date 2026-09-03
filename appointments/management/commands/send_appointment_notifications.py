from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from appointments.notifications import deliver_pending_notifications


class Command(BaseCommand):
    help = "Send and retry queued staff-only appointment notifications."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=25)

    def handle(self, *args, **options):
        if not settings.APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED:
            self.stdout.write("appointment_notifications=disabled")
            return
        if options["limit"] < 1 or options["limit"] > 250:
            raise CommandError("--limit must be between 1 and 250.")

        results = deliver_pending_notifications(limit=options["limit"])
        for name, count in results.items():
            self.stdout.write(f"{name}={count}")
        if results["retrying"]:
            raise CommandError(
                f"appointment_notification_retries={results['retrying']}"
            )
