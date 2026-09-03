import uuid

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a privacy-safe SMTP test to configured appointment recipients."

    def handle(self, *args, **options):
        if not settings.APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED:
            raise CommandError("Appointment email notifications are disabled.")

        sent = 0
        for recipient in settings.APPOINTMENT_NOTIFICATION_RECIPIENTS:
            reference = uuid.uuid4()
            message = EmailMessage(
                subject="Arya Skin Clinic appointment notification test",
                body=(
                    "This is a configuration test. It contains no appointment or "
                    "patient information. No action is required."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                headers={
                    "Resend-Idempotency-Key": (
                        f"appointment-notification-test/{reference}"
                    ),
                    "X-Entity-Ref-ID": str(reference),
                },
            )
            try:
                sent_count = message.send(fail_silently=False)
                if sent_count != 1:
                    raise RuntimeError("Email backend did not confirm delivery.")
            except Exception as error:
                raise CommandError(
                    f"Appointment notification test failed ({type(error).__name__})."
                ) from None
            sent += 1

        self.stdout.write(f"test_notifications_sent={sent}")
