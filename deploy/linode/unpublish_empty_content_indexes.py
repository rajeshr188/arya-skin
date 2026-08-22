from django.db import transaction

from blog.models import BlogIndexPage, BlogPage
from treatments.models import TreatmentIndexPage, TreatmentPage


def assert_empty_index(index, child_model, expected_slug):
    if index.slug != expected_slug:
        raise RuntimeError(
            f"Expected slug {expected_slug!r}, found {index.slug!r}."
        )
    if not index.live:
        raise RuntimeError(f"{index.title} is already unpublished.")
    if index.has_unpublished_changes:
        raise RuntimeError(
            f"{index.title} has unpublished changes; review them before continuing."
        )

    descendants = child_model.objects.descendant_of(index)
    total = descendants.count()
    live = descendants.live().count()
    if total or live:
        raise RuntimeError(
            f"Refusing to unpublish {index.title}: found {total} child records "
            f"({live} live)."
        )


with transaction.atomic():
    treatment_index = TreatmentIndexPage.objects.select_for_update().get(
        slug="treatments"
    )
    blog_index = BlogIndexPage.objects.select_for_update().get(slug="blog")

    assert_empty_index(treatment_index, TreatmentPage, "treatments")
    assert_empty_index(blog_index, BlogPage, "blog")

    treatment_index.unpublish(log_action=True)
    blog_index.unpublish(log_action=True)

    treatment_index.refresh_from_db()
    blog_index.refresh_from_db()
    if treatment_index.live or blog_index.live:
        raise RuntimeError("One or more empty content indexes remain live.")

print("treatments=unpublished")
print("articles=unpublished")
