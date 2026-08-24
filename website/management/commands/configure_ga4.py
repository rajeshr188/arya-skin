import re
from copy import deepcopy

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from website.models import SiteSettings, StandardPage


MEASUREMENT_ID_PATTERN = re.compile(r"G-[A-Z0-9]+")
OLD_ANALYTICS_NOTICE = (
    "Optional analytics is currently disabled. If analytics is introduced later, "
    "this notice and the website's consent controls must be updated before it is "
    "enabled."
)
NEW_ANALYTICS_NOTICE = (
    "Optional Google Analytics is loaded only after a visitor selects Allow "
    "analytics in the website's consent banner. It helps the clinic understand "
    "visits to public pages and approved contact actions. When allowed, Google "
    "Analytics may set cookies and use similar browser storage, and may process "
    "technical and usage information including page and clinic identifiers, device "
    "and browser information, approximate location derived from an IP address, and "
    "the approved interaction events described here. The website does not send "
    "appointment form contents, names, phone numbers, email addresses, messages, "
    "medical concerns, or other patient information to Google Analytics. Advertising "
    "storage, ad user data, ad personalization, Google Signals, User-ID, enhanced "
    "conversions, and automatic form or outbound-link measurement are disabled. "
    "Analytics is optional, and the website and appointment form work if it is "
    "declined. A visitor may decline when the banner appears or later reopen "
    "Analytics choices in the footer and withdraw consent. The browser remembers the "
    "choice locally. The clinic uses the two-month Google Analytics user-level and "
    "event-level data retention setting; standard aggregated reports may remain "
    "available under Google's service terms. Google processes analytics information "
    "under its own terms and privacy practices."
)


def replace_in_value(value):
    if isinstance(value, str):
        return (
            value.replace(OLD_ANALYTICS_NOTICE, NEW_ANALYTICS_NOTICE),
            value.count(OLD_ANALYTICS_NOTICE),
            value.count(NEW_ANALYTICS_NOTICE),
        )
    if isinstance(value, list):
        replaced = []
        old_count = 0
        new_count = 0
        for item in value:
            new_item, item_old_count, item_new_count = replace_in_value(item)
            replaced.append(new_item)
            old_count += item_old_count
            new_count += item_new_count
        return replaced, old_count, new_count
    if isinstance(value, dict):
        replaced = {}
        old_count = 0
        new_count = 0
        for key, item in value.items():
            new_item, item_old_count, item_new_count = replace_in_value(item)
            replaced[key] = new_item
            old_count += item_old_count
            new_count += item_new_count
        return replaced, old_count, new_count
    return value, 0, 0


class Command(BaseCommand):
    help = (
        "Publish the approved Google Analytics privacy wording and configure a GA4 "
        "measurement ID. Analytics remains disabled unless --enable is supplied."
    )

    def add_arguments(self, parser):
        parser.add_argument("measurement_id")
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable GA4 after its account-side privacy controls are confirmed.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        measurement_id = options["measurement_id"].strip().upper()
        if not MEASUREMENT_ID_PATTERN.fullmatch(measurement_id):
            raise CommandError("Enter a GA4 measurement ID such as G-XXXXXXXXXX.")

        page = StandardPage.objects.select_for_update().get(slug="privacy")
        if not page.live:
            raise CommandError("Privacy page is not live; refusing configuration.")
        if page.has_unpublished_changes:
            raise CommandError(
                "Privacy page has unpublished changes; review them before configuration."
            )

        introduction, introduction_old, introduction_new = replace_in_value(
            str(page.introduction)
        )
        body_field = page._meta.get_field("body")
        serialized_body = body_field.get_prep_value(page.body)
        body_data, body_old, body_new = replace_in_value(
            deepcopy(serialized_body)
        )
        old_count = introduction_old + body_old
        new_count = introduction_new + body_new

        privacy_revision = None
        if old_count == 1 and new_count == 0:
            page.introduction = introduction
            page.body = body_data
            page.full_clean()
            privacy_revision = page.save_revision(log_action=True)
            privacy_revision.publish()
        elif old_count != 0 or new_count != 1:
            raise CommandError(
                "Privacy analytics wording did not match the approved old or new text; "
                "manual review is required."
            )

        page.refresh_from_db()
        site = page.get_site()
        settings = SiteSettings.objects.select_for_update().get(site=site)
        existing_ga4 = settings.google_analytics_id.strip().upper()
        existing_gtm = settings.google_tag_manager_id.strip().upper()
        if existing_ga4 and existing_ga4 != measurement_id:
            raise CommandError("A different GA4 measurement ID is already configured.")
        if existing_gtm:
            raise CommandError("A Tag Manager container is already configured.")

        settings.google_analytics_id = measurement_id
        settings.google_tag_manager_id = ""
        settings.analytics_enabled = options["enable"]
        settings.full_clean()
        settings.save()

        self.stdout.write(
            f"privacy_revision={privacy_revision.id if privacy_revision else 'unchanged'}"
        )
        self.stdout.write(f"measurement_id={measurement_id}")
        self.stdout.write(
            f"analytics_enabled={str(settings.analytics_enabled).lower()}"
        )
