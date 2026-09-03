import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from .models import AppointmentNotificationDelivery


logger = logging.getLogger(__name__)

RETRY_DELAYS = (
    timedelta(minutes=1),
    timedelta(minutes=5),
    timedelta(minutes=15),
    timedelta(hours=1),
    timedelta(hours=6),
)


def queue_appointment_notifications(enquiry):
    if not settings.APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED:
        return []
    return [
        AppointmentNotificationDelivery.objects.get_or_create(
            enquiry=enquiry,
            recipient=recipient,
        )[0]
        for recipient in settings.APPOINTMENT_NOTIFICATION_RECIPIENTS
    ]


def _notification_message(delivery):
    enquiry = delivery.enquiry
    received_at = timezone.localtime(enquiry.created_at).strftime(
        "%d %B %Y at %I:%M %p %Z"
    )
    admin_url = (
        settings.WAGTAILADMIN_BASE_URL.rstrip("/")
        + "/admin/appointments/appointmentenquiry/"
    )
    return EmailMessage(
        subject=f"New appointment enquiry - {enquiry.clinic_name}",
        body=(
            f"A new appointment enquiry was received for {enquiry.clinic_name}.\n\n"
            f"Received: {received_at}\n\n"
            "Sign in securely to review and respond:\n"
            f"{admin_url}\n\n"
            "Patient details are intentionally excluded from this email. "
            "The request is not a confirmed appointment."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[delivery.recipient],
        headers={
            "Resend-Idempotency-Key": (
                f"appointment-notification/{delivery.reference}"
            ),
            "X-Entity-Ref-ID": str(delivery.reference),
        },
    )


def _next_retry(attempts):
    index = min(max(attempts - 1, 0), len(RETRY_DELAYS) - 1)
    return timezone.now() + RETRY_DELAYS[index]


def deliver_pending_notifications(limit=25):
    results = {"attempted": 0, "sent": 0, "retrying": 0}
    for _ in range(limit):
        with transaction.atomic():
            delivery = (
                AppointmentNotificationDelivery.objects.select_for_update(
                    skip_locked=True
                )
                .select_related("enquiry")
                .filter(
                    status__in=(
                        AppointmentNotificationDelivery.Status.PENDING,
                        AppointmentNotificationDelivery.Status.RETRYING,
                    ),
                    recipient__in=settings.APPOINTMENT_NOTIFICATION_RECIPIENTS,
                    next_attempt_at__lte=timezone.now(),
                )
                .order_by("next_attempt_at", "pk")
                .first()
            )
            if delivery is None:
                break

            results["attempted"] += 1
            delivery.attempts += 1
            delivery.last_attempt_at = timezone.now()
            try:
                sent_count = _notification_message(delivery).send(
                    fail_silently=False
                )
                if sent_count != 1:
                    raise RuntimeError("Email backend did not confirm delivery.")
            except Exception as error:
                delivery.status = AppointmentNotificationDelivery.Status.RETRYING
                delivery.next_attempt_at = _next_retry(delivery.attempts)
                delivery.last_error_type = type(error).__name__[:120]
                delivery.save(
                    update_fields=(
                        "attempts",
                        "last_attempt_at",
                        "status",
                        "next_attempt_at",
                        "last_error_type",
                        "updated_at",
                    )
                )
                results["retrying"] += 1
                logger.warning(
                    "Appointment notification delivery failed",
                    extra={"delivery_id": delivery.pk},
                )
                continue

            delivery.status = AppointmentNotificationDelivery.Status.SENT
            delivery.sent_at = timezone.now()
            delivery.next_attempt_at = delivery.sent_at
            delivery.last_error_type = ""
            delivery.save(
                update_fields=(
                    "attempts",
                    "last_attempt_at",
                    "status",
                    "sent_at",
                    "next_attempt_at",
                    "last_error_type",
                    "updated_at",
                )
            )
            results["sent"] += 1
            logger.info(
                "Appointment notification delivered",
                extra={"delivery_id": delivery.pk},
            )
    return results
