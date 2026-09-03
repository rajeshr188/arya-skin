from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from website.management.commands.update_appointment_email_privacy import (
    NEW_SHARING_NOTICE,
    OLD_SHARING_NOTICE,
)
from website.models import StandardPage


class TransactionalEmailPrivacyTests(TestCase):
    def test_privacy_update_publishes_once_and_is_repeat_safe(self):
        page = StandardPage.objects.get(slug="privacy")
        page.body = [
            (
                "rich_text",
                "<h2>Sharing and security</h2>"
                f"<p>{OLD_SHARING_NOTICE} It is not sold.</p>",
            )
        ]
        page.save_revision().publish()

        output = StringIO()
        call_command("update_appointment_email_privacy", stdout=output)

        page.refresh_from_db()
        self.assertIn(NEW_SHARING_NOTICE, str(page.body))
        self.assertIn("appointment_email_privacy=published", output.getvalue())

        rerun_output = StringIO()
        call_command(
            "update_appointment_email_privacy", stdout=rerun_output
        )
        self.assertIn("privacy_revision=unchanged", rerun_output.getvalue())
