from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from clinics.models import ClinicIndexPage, ClinicPage

from .forms import CONSENT_VERSION
from .models import AppointmentEnquiry, AppointmentNotificationDelivery


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class AppointmentEnquiryTests(TestCase):
    def setUp(self):
        self.clinic_index = ClinicIndexPage.objects.get()
        self.sitapura = ClinicPage.objects.get(slug="sitapura")
        self.chaksu = ClinicPage.objects.get(slug="chaksu")

    def publish_clinic(self, clinic):
        if not self.clinic_index.live:
            self.clinic_index.save_revision().publish()
        clinic.save_revision().publish()
        clinic.refresh_from_db()
        return clinic

    def valid_payload(self, response, clinic=None, **overrides):
        payload = {
            "clinic": (clinic or self.sitapura).pk,
            "name": "Test Patient",
            "phone": "+91 98765 43210",
            "email": "patient@example.com",
            "preferred_date": (timezone.localdate() + timedelta(days=3)).isoformat(),
            "time_preference": AppointmentEnquiry.TimePreference.MORNING,
            "consent_to_contact": "on",
            "form_token": response.context["form"].initial["form_token"],
            "website": "",
        }
        payload.update(overrides)
        return payload

    def test_request_routes_require_a_published_clinic(self):
        self.assertEqual(self.client.get(reverse("appointments:request")).status_code, 404)
        self.assertEqual(
            self.client.get(
                reverse(
                    "appointments:request_for_clinic",
                    kwargs={"clinic_slug": "sitapura"},
                )
            ).status_code,
            404,
        )

    def test_form_collects_only_minimum_operational_details(self):
        self.publish_clinic(self.sitapura)

        response = self.client.get(reverse("appointments:request"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("no-cache", response.headers["Cache-Control"])
        self.assertContains(response, "within one business day")
        self.assertContains(response, "must not be used for emergencies")
        field_names = set(response.context["form"].fields)
        self.assertEqual(
            field_names,
            {
                "clinic",
                "name",
                "phone",
                "email",
                "preferred_date",
                "time_preference",
                "consent_to_contact",
                "form_token",
                "website",
            },
        )
        self.assertFalse(
            {"medical_concern", "diagnosis", "date_of_birth", "address"}
            & field_names
        )

    def test_valid_request_is_saved_and_redirected(self):
        self.publish_clinic(self.sitapura)
        form_response = self.client.get(
            reverse(
                "appointments:request_for_clinic",
                kwargs={"clinic_slug": "sitapura"},
            )
        )

        response = self.client.post(
            form_response.request["PATH_INFO"],
            self.valid_payload(form_response),
        )

        self.assertRedirects(response, reverse("appointments:success"))
        enquiry = AppointmentEnquiry.objects.get()
        self.assertEqual(enquiry.clinic, self.sitapura)
        self.assertEqual(enquiry.clinic_name, "Dolphin Derma Care")
        self.assertEqual(enquiry.status, AppointmentEnquiry.Status.NEW)
        self.assertTrue(enquiry.consent_to_contact)
        self.assertEqual(enquiry.consent_version, CONSENT_VERSION)
        self.assertEqual(enquiry.source_path, "/appointments/request/sitapura/")
        self.assertNotIn("patient@example.com", response.url)

    @override_settings(
        APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED=True,
        APPOINTMENT_NOTIFICATION_RECIPIENTS=("doctor-notifications@example.com",),
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL=(
            "Arya Skin Clinic <appointments@notify.drnareshrathod.com>"
        ),
        WAGTAILADMIN_BASE_URL="https://drnareshrathod.com",
    )
    def test_notification_is_queued_then_sent_without_patient_details(self):
        self.publish_clinic(self.sitapura)
        url = reverse(
            "appointments:request_for_clinic",
            kwargs={"clinic_slug": "sitapura"},
        )
        form_response = self.client.get(url)

        response = self.client.post(url, self.valid_payload(form_response))

        self.assertRedirects(response, reverse("appointments:success"))
        delivery = AppointmentNotificationDelivery.objects.get()
        self.assertEqual(
            delivery.status, AppointmentNotificationDelivery.Status.PENDING
        )
        self.assertEqual(len(mail.outbox), 0)

        output = StringIO()
        call_command("send_appointment_notifications", stdout=output)

        delivery.refresh_from_db()
        self.assertEqual(
            delivery.status, AppointmentNotificationDelivery.Status.SENT
        )
        self.assertEqual(delivery.attempts, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["doctor-notifications@example.com"])
        self.assertIn("Dolphin Derma Care", message.subject)
        self.assertIn(
            "https://drnareshrathod.com/admin/appointments/appointmentenquiry/",
            message.body,
        )
        for patient_value in (
            "Test Patient",
            "+91 98765 43210",
            "patient@example.com",
            (timezone.localdate() + timedelta(days=3)).isoformat(),
            "/appointments/request/sitapura/",
            str(delivery.enquiry.reference),
        ):
            self.assertNotIn(patient_value, message.body)
            self.assertNotIn(patient_value, message.subject)
        self.assertEqual(
            message.extra_headers["Resend-Idempotency-Key"],
            f"appointment-notification/{delivery.reference}",
        )
        self.assertIn("sent=1", output.getvalue())

        call_command("send_appointment_notifications", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(
        APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED=True,
        APPOINTMENT_NOTIFICATION_RECIPIENTS=("doctor-notifications@example.com",),
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL=(
            "Arya Skin Clinic <appointments@notify.drnareshrathod.com>"
        ),
        WAGTAILADMIN_BASE_URL="https://drnareshrathod.com",
    )
    def test_notification_failure_is_retried_without_losing_enquiry_or_error_text(self):
        self.publish_clinic(self.sitapura)
        url = reverse("appointments:request")
        form_response = self.client.get(url)
        self.client.post(url, self.valid_payload(form_response))

        with patch(
            "appointments.notifications.EmailMessage.send",
            side_effect=TimeoutError("patient@example.com must not reach logs"),
        ):
            with self.assertRaises(CommandError):
                call_command("send_appointment_notifications", stdout=StringIO())

        self.assertEqual(AppointmentEnquiry.objects.count(), 1)
        delivery = AppointmentNotificationDelivery.objects.get()
        self.assertEqual(
            delivery.status, AppointmentNotificationDelivery.Status.RETRYING
        )
        self.assertEqual(delivery.attempts, 1)
        self.assertEqual(delivery.last_error_type, "TimeoutError")
        self.assertNotIn("patient@example.com", delivery.last_error_type)
        self.assertGreater(delivery.next_attempt_at, timezone.now())

        immediate_output = StringIO()
        call_command("send_appointment_notifications", stdout=immediate_output)
        self.assertIn("attempted=0", immediate_output.getvalue())

        AppointmentNotificationDelivery.objects.filter(pk=delivery.pk).update(
            next_attempt_at=timezone.now() - timedelta(seconds=1)
        )
        call_command("send_appointment_notifications", stdout=StringIO())
        delivery.refresh_from_db()
        self.assertEqual(
            delivery.status, AppointmentNotificationDelivery.Status.SENT
        )
        self.assertEqual(delivery.attempts, 2)

    @override_settings(
        APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED=True,
        APPOINTMENT_NOTIFICATION_RECIPIENTS=("doctor-notifications@example.com",),
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL=(
            "Arya Skin Clinic <appointments@notify.drnareshrathod.com>"
        ),
    )
    def test_removed_recipient_does_not_receive_a_queued_notification(self):
        self.publish_clinic(self.sitapura)
        url = reverse("appointments:request")
        form_response = self.client.get(url)
        self.client.post(url, self.valid_payload(form_response))

        with override_settings(APPOINTMENT_NOTIFICATION_RECIPIENTS=()):
            output = StringIO()
            call_command("send_appointment_notifications", stdout=output)

        self.assertIn("attempted=0", output.getvalue())
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            AppointmentNotificationDelivery.objects.get().status,
            AppointmentNotificationDelivery.Status.PENDING,
        )

    def test_notification_is_not_queued_while_feature_is_disabled(self):
        self.publish_clinic(self.sitapura)
        url = reverse("appointments:request")
        form_response = self.client.get(url)

        self.client.post(url, self.valid_payload(form_response))

        self.assertEqual(AppointmentEnquiry.objects.count(), 1)
        self.assertEqual(AppointmentNotificationDelivery.objects.count(), 0)

    @override_settings(
        APPOINTMENT_EMAIL_NOTIFICATIONS_ENABLED=True,
        APPOINTMENT_NOTIFICATION_RECIPIENTS=("doctor-notifications@example.com",),
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL=(
            "Arya Skin Clinic <appointments@notify.drnareshrathod.com>"
        ),
    )
    def test_configuration_test_email_contains_no_enquiry_data(self):
        output = StringIO()

        call_command("send_appointment_notification_test", stdout=output)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["doctor-notifications@example.com"])
        self.assertIn("no appointment or patient information", mail.outbox[0].body)
        self.assertIn("test_notifications_sent=1", output.getvalue())

    def test_fixed_clinic_cannot_be_changed_by_post_data(self):
        self.publish_clinic(self.sitapura)
        self.publish_clinic(self.chaksu)
        url = reverse(
            "appointments:request_for_clinic",
            kwargs={"clinic_slug": "sitapura"},
        )
        form_response = self.client.get(url)

        response = self.client.post(
            url,
            self.valid_payload(form_response, clinic=self.chaksu),
        )

        self.assertRedirects(response, reverse("appointments:success"))
        self.assertEqual(AppointmentEnquiry.objects.get().clinic, self.sitapura)

    def test_invalid_or_spam_submission_is_not_saved(self):
        self.publish_clinic(self.sitapura)
        url = reverse("appointments:request")

        cases = (
            {"phone": "123"},
            {"preferred_date": (timezone.localdate() - timedelta(days=1)).isoformat()},
            {"consent_to_contact": ""},
            {"form_token": "invalid"},
            {"website": "bot-filled.example"},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                form_response = self.client.get(url)
                response = self.client.post(
                    url,
                    self.valid_payload(form_response, **overrides),
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(AppointmentEnquiry.objects.count(), 0)

    @override_settings(APPOINTMENT_SUBMISSION_LIMIT=1)
    def test_session_rate_limit_rejects_repeated_submission(self):
        self.publish_clinic(self.sitapura)
        url = reverse("appointments:request")
        first_form = self.client.get(url)
        self.client.post(url, self.valid_payload(first_form))
        second_form = self.client.get(url)

        response = self.client.post(url, self.valid_payload(second_form))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Too many requests have been submitted")
        self.assertEqual(AppointmentEnquiry.objects.count(), 1)

    def test_csrf_is_required(self):
        self.publish_clinic(self.sitapura)
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(reverse("appointments:request"), {})

        self.assertEqual(response.status_code, 403)

    def test_success_page_contains_no_submitted_personal_data(self):
        self.sitapura.phone = "9461289316"
        self.sitapura.phone_is_public = True
        self.sitapura.whatsapp = "+919461289316"
        self.sitapura.whatsapp_is_public = True
        self.publish_clinic(self.sitapura)
        session = self.client.session
        session["appointment_request_submitted"] = True
        session["appointment_request_clinic_slug"] = self.sitapura.slug
        session.save()
        response = self.client.get(reverse("appointments:success"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "within one business day")
        self.assertContains(response, "does not confirm an appointment")
        self.assertContains(response, "must not be used for emergencies")
        self.assertContains(response, 'href="tel:')
        self.assertContains(response, "Call Dolphin Derma Care")
        self.assertContains(response, "WhatsApp Dolphin Derma Care")
        self.assertNotContains(response, "Test Patient")

    def test_success_page_does_not_claim_an_unsubmitted_request(self):
        response = self.client.get(reverse("appointments:success"))

        self.assertRedirects(response, "/")

    def test_admin_requires_staff_authentication(self):
        admin_url = reverse("admin:appointments_appointmentenquiry_changelist")
        anonymous_response = self.client.get(admin_url)
        self.assertEqual(anonymous_response.status_code, 302)

        user = get_user_model().objects.create_superuser(
            username="appointment-admin",
            email="admin@example.com",
            password="test-password-123",
        )
        self.client.force_login(user)
        staff_response = self.client.get(admin_url)

        self.assertEqual(staff_response.status_code, 200)
        self.assertContains(staff_response, "Appointment enquiries")

    def test_closed_enquiries_are_deleted_after_approved_retention(self):
        now = timezone.now()
        old_closed = AppointmentEnquiry.objects.create(
            clinic=self.sitapura,
            name="Old Closed",
            phone="9876543210",
            preferred_date=timezone.localdate(),
            consent_to_contact=True,
            consent_version=CONSENT_VERSION,
            status=AppointmentEnquiry.Status.CLOSED,
        )
        recent_closed = AppointmentEnquiry.objects.create(
            clinic=self.sitapura,
            name="Recent Closed",
            phone="9876543211",
            preferred_date=timezone.localdate(),
            consent_to_contact=True,
            consent_version=CONSENT_VERSION,
            status=AppointmentEnquiry.Status.CLOSED,
        )
        old_open = AppointmentEnquiry.objects.create(
            clinic=self.sitapura,
            name="Old Open",
            phone="9876543212",
            preferred_date=timezone.localdate(),
            consent_to_contact=True,
            consent_version=CONSENT_VERSION,
            status=AppointmentEnquiry.Status.CONTACTED,
        )
        AppointmentEnquiry.objects.filter(pk=old_closed.pk).update(
            updated_at=now - timedelta(days=91)
        )
        AppointmentEnquiry.objects.filter(pk=old_open.pk).update(
            updated_at=now - timedelta(days=91)
        )

        output = StringIO()
        call_command("purge_closed_enquiries", stdout=output)

        self.assertFalse(AppointmentEnquiry.objects.filter(pk=old_closed.pk).exists())
        self.assertTrue(
            AppointmentEnquiry.objects.filter(pk=recent_closed.pk).exists()
        )
        self.assertTrue(AppointmentEnquiry.objects.filter(pk=old_open.pk).exists())
        self.assertIn("deleted_closed_enquiries=1", output.getvalue())

    def test_retention_command_supports_a_dry_run(self):
        enquiry = AppointmentEnquiry.objects.create(
            clinic=self.sitapura,
            name="Dry Run",
            phone="9876543213",
            preferred_date=timezone.localdate(),
            consent_to_contact=True,
            consent_version=CONSENT_VERSION,
            status=AppointmentEnquiry.Status.CLOSED,
        )
        AppointmentEnquiry.objects.filter(pk=enquiry.pk).update(
            updated_at=timezone.now() - timedelta(days=91)
        )

        output = StringIO()
        call_command("purge_closed_enquiries", dry_run=True, stdout=output)

        self.assertTrue(AppointmentEnquiry.objects.filter(pk=enquiry.pk).exists())
        self.assertIn("eligible_closed_enquiries=1", output.getvalue())

    def test_clinic_page_has_desktop_and_mobile_conversion_actions(self):
        self.publish_clinic(self.sitapura)

        response = self.client.get("/clinics/sitapura/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'href="/appointments/request/sitapura/"',
            count=2,
        )
        self.assertNotContains(response, "Call clinic")
        self.assertNotContains(response, "Chat on WhatsApp")
        self.assertNotContains(response, "Get directions")
