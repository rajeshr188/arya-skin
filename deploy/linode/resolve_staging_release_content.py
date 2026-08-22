from datetime import time

from django.db import transaction

from clinics.models import ClinicIndexPage, ClinicPage


def clinic_index_public_fields(page):
    return {
        "title": page.title,
        "slug": page.slug,
        "show_in_menus": page.show_in_menus,
        "seo_title": page.seo_title,
        "search_description": page.search_description,
        "introduction": str(page.introduction),
    }


with transaction.atomic():
    clinic_index = ClinicIndexPage.objects.select_for_update().get(slug="clinics")
    if not clinic_index.live or not clinic_index.has_unpublished_changes:
        raise RuntimeError("Expected a live Clinics index with unpublished changes.")
    live_object = clinic_index.live_revision.as_object()
    latest_revision = clinic_index.get_latest_revision()
    latest_object = latest_revision.as_object()
    if clinic_index_public_fields(live_object) != clinic_index_public_fields(
        latest_object
    ):
        raise RuntimeError("Clinics index revisions differ; manual review is required.")
    latest_revision.publish()

    chaksu = ClinicPage.objects.select_for_update().get(slug="chaksu")
    if not chaksu.live or chaksu.has_unpublished_changes:
        raise RuntimeError("Chaksu page is not in the expected published state.")
    monday = chaksu.opening_hours.select_for_update().get(day="monday")
    if not (
        monday.is_closed
        and monday.opens_at == time(17, 0)
        and monday.closes_at == time(18, 0)
    ):
        raise RuntimeError("Chaksu Monday hours do not match the audited conflict.")
    monday.opens_at = None
    monday.closes_at = None
    monday.save(update_fields=["opens_at", "closes_at"])
    chaksu_revision = chaksu.save_revision(log_action=True)
    chaksu_revision.publish()

    clinic_index.refresh_from_db()
    chaksu.refresh_from_db()
    monday.refresh_from_db()
    if clinic_index.has_unpublished_changes:
        raise RuntimeError("Clinics index still has unpublished changes.")
    if chaksu.has_unpublished_changes or monday.opens_at or monday.closes_at:
        raise RuntimeError("Chaksu Monday cleanup did not publish correctly.")

print(f"clinic_index_revision={latest_revision.id}")
print("clinic_index_draft_conflict=resolved")
print(f"chaksu_revision={chaksu_revision.id}")
print("chaksu_monday=closed_without_hidden_times")
