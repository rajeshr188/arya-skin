from copy import deepcopy

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from website.models import StandardPage


OLD_SHARING_NOTICE = (
    "Information may also be processed by hosting, backup, or technical providers "
    "strictly to operate and secure the website, or disclosed where legally "
    "required."
)
NEW_SHARING_NOTICE = (
    "Information may also be processed by hosting, backup, or technical providers "
    "strictly to operate and secure the website. The transactional email provider "
    "processes the designated staff recipient address and a notification containing "
    "the clinic name, received time, and secure administration link; patient-entered "
    "appointment details are intentionally excluded. Information may also be "
    "disclosed where legally required."
)


def replace_in_value(value):
    if isinstance(value, str):
        return (
            value.replace(OLD_SHARING_NOTICE, NEW_SHARING_NOTICE),
            value.count(OLD_SHARING_NOTICE),
            value.count(NEW_SHARING_NOTICE),
        )
    if isinstance(value, list):
        replaced = []
        old_count = 0
        new_count = 0
        for item in value:
            new_item, item_old, item_new = replace_in_value(item)
            replaced.append(new_item)
            old_count += item_old
            new_count += item_new
        return replaced, old_count, new_count
    if isinstance(value, dict):
        replaced = {}
        old_count = 0
        new_count = 0
        for key, item in value.items():
            new_item, item_old, item_new = replace_in_value(item)
            replaced[key] = new_item
            old_count += item_old
            new_count += item_new
        return replaced, old_count, new_count
    return value, 0, 0


class Command(BaseCommand):
    help = "Publish the approved privacy wording for staff email notifications."

    @transaction.atomic
    def handle(self, *args, **options):
        page = StandardPage.objects.select_for_update().get(slug="privacy")
        if not page.live:
            raise CommandError("Privacy page is not live; refusing update.")
        if page.has_unpublished_changes:
            raise CommandError(
                "Privacy page has unpublished changes; review them before updating."
            )

        introduction, introduction_old, introduction_new = replace_in_value(
            str(page.introduction)
        )
        body_field = page._meta.get_field("body")
        body_data, body_old, body_new = replace_in_value(
            deepcopy(body_field.get_prep_value(page.body))
        )
        old_count = introduction_old + body_old
        new_count = introduction_new + body_new

        revision = None
        if old_count == 1 and new_count == 0:
            page.introduction = introduction
            page.body = body_data
            page.full_clean()
            revision = page.save_revision(log_action=True)
            revision.publish()
        elif old_count != 0 or new_count != 1:
            raise CommandError(
                "Privacy sharing wording did not match the approved old or new text; "
                "manual review is required."
            )

        self.stdout.write(
            f"privacy_revision={revision.id if revision else 'unchanged'}"
        )
        self.stdout.write("appointment_email_privacy=published")
