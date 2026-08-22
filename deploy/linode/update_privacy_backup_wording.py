from copy import deepcopy

from website.models import StandardPage


OLD_SENTENCE = (
    "A deleted record may remain in a restricted local backup for up to 14 "
    "additional days before that backup expires."
)
NEW_SENTENCE = (
    "A deleted record may remain in a restricted local backup or a client-side "
    "encrypted off-server backup for up to 14 additional days before that "
    "backup expires."
)


def replace_in_value(value):
    if isinstance(value, str):
        return value.replace(OLD_SENTENCE, NEW_SENTENCE), value.count(OLD_SENTENCE)
    if isinstance(value, list):
        replaced = []
        count = 0
        for item in value:
            new_item, item_count = replace_in_value(item)
            replaced.append(new_item)
            count += item_count
        return replaced, count
    if isinstance(value, dict):
        replaced = {}
        count = 0
        for key, item in value.items():
            new_item, item_count = replace_in_value(item)
            replaced[key] = new_item
            count += item_count
        return replaced, count
    return value, 0


page = StandardPage.objects.get(slug="privacy")
if not page.live:
    raise RuntimeError("Privacy page is not live; refusing automatic publication.")
if page.has_unpublished_changes:
    raise RuntimeError(
        "Privacy page has unrelated unpublished changes; resolve them first."
    )

introduction, introduction_count = replace_in_value(str(page.introduction))
body_data, body_count = replace_in_value(deepcopy(page.body.raw_data))
replacement_count = introduction_count + body_count
if replacement_count != 1:
    raise RuntimeError(
        f"Expected exactly one approved sentence, found {replacement_count}."
    )

page.introduction = introduction
page.body = body_data
page.full_clean()
revision = page.save_revision(log_action=True)
revision.publish()

page.refresh_from_db()
rendered_values = str(page.introduction) + repr(page.body.raw_data)
if OLD_SENTENCE in rendered_values or NEW_SENTENCE not in rendered_values:
    raise RuntimeError("Published Privacy revision did not retain approved wording.")

print(f"privacy_revision={revision.id}")
print(f"privacy_url={page.url}")
print("privacy_backup_wording=published")
