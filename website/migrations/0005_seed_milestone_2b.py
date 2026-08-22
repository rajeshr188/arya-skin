from django.db import migrations


def seed_milestone_2b(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page

    TreatmentIndexPage = apps.get_model("treatments", "TreatmentIndexPage")
    ContactPage = apps.get_model("website", "ContactPage")
    HomePage = apps.get_model("website", "HomePage")
    StandardPage = apps.get_model("website", "StandardPage")

    home_record = HomePage.objects.first()
    if not home_record:
        return

    home_record.hero_eyebrow = "Dermatology and cosmetology consultations in Jaipur"
    home_record.introduction = (
        "<p>Consultations with Dr. Naresh Rathod are available in Sitapura and "
        "Chaksu, Jaipur.</p>"
    )
    home_record.concerns_heading = "Patient information"
    home_record.doctor_section_heading = "Meet Dr. Naresh Rathod"
    home_record.clinic_section_heading = "Clinic locations"
    home_record.faq_heading = "Frequently asked questions"
    home_record.final_cta_heading = "Contact a clinic"
    home_record.final_cta_text = "Choose a clinic to view its verified contact details."
    home_record.save()
    home = Page.objects.get(pk=home_record.pk)

    def page_content_type(model):
        return ContentType.objects.get_or_create(
            app_label=model._meta.app_label,
            model=model._meta.model_name,
        )[0]

    if not TreatmentIndexPage.objects.exists():
        page = TreatmentIndexPage(
            title="Treatments",
            slug="treatments",
            show_in_menus=True,
            live=False,
            has_unpublished_changes=True,
            content_type_id=page_content_type(TreatmentIndexPage).pk,
            locale_id=home.locale_id,
            url_path=f"{home.url_path}treatments/",
        )
        home.add_child(instance=page)

    if not ContactPage.objects.exists():
        page = ContactPage(
            title="Contact",
            slug="contact",
            show_in_menus=True,
            live=False,
            has_unpublished_changes=True,
            content_type_id=page_content_type(ContactPage).pk,
            locale_id=home.locale_id,
            url_path=f"{home.url_path}contact/",
        )
        home.add_child(instance=page)

    for title, slug in (
        ("Privacy", "privacy"),
        ("Medical disclaimer", "medical-disclaimer"),
    ):
        if not StandardPage.objects.filter(slug=slug).exists():
            page = StandardPage(
                title=title,
                slug=slug,
                show_in_menus=False,
                live=False,
                has_unpublished_changes=True,
                content_type_id=page_content_type(StandardPage).pk,
                locale_id=home.locale_id,
                url_path=f"{home.url_path}{slug}/",
            )
            home.add_child(instance=page)


class Migration(migrations.Migration):
    dependencies = [
        ("treatments", "0001_initial"),
        ("website", "0004_contactpage_standardpage_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_milestone_2b, migrations.RunPython.noop),
    ]
