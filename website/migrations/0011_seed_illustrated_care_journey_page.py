from django.db import migrations


def seed_illustrated_care_journey_page(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page

    IllustratedCareJourneyPage = apps.get_model(
        "website", "IllustratedCareJourneyPage"
    )
    HomePage = apps.get_model("website", "HomePage")

    home_record = HomePage.objects.first()
    if not home_record or IllustratedCareJourneyPage.objects.exists():
        return

    home = Page.objects.get(pk=home_record.pk)
    content_type = ContentType.objects.get_or_create(
        app_label="website",
        model="illustratedcarejourneypage",
    )[0]
    page = IllustratedCareJourneyPage(
        title="Illustrated care journeys",
        slug="illustrated-care-journeys",
        show_in_menus=True,
        live=False,
        has_unpublished_changes=True,
        content_type_id=content_type.pk,
        locale_id=home.locale_id,
        url_path=f"{home.url_path}illustrated-care-journeys/",
    )
    home.add_child(instance=page)


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0010_illustratedcarejourneypage_and_more"),
    ]

    operations = [
        migrations.RunPython(
            seed_illustrated_care_journey_page,
            migrations.RunPython.noop,
        ),
    ]
