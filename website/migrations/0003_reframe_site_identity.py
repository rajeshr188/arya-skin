from django.db import migrations, models


def reframe_site_identity(apps, schema_editor):
    from wagtail.models import Site

    HomePage = apps.get_model("website", "HomePage")
    SiteSettings = apps.get_model("website", "SiteSettings")

    SiteSettings.objects.update(
        site_title="Dr. Naresh Rathod - Dermatologist",
        doctor_name="Dr. Naresh Rathod",
        professional_title="Dermatologist and Cosmetologist",
        location_summary=(
            "Dolphin Derma Care - Sitapura | "
            "Arya Skin and Hair Clinic - Chaksu | Jaipur"
        ),
    )

    home = HomePage.objects.first()
    if home:
        home.title = "Dr. Naresh Rathod"
        home.seo_title = "Dr. Naresh Rathod - Dermatologist and Cosmetologist in Jaipur"
        home.search_description = (
            "Dr. Naresh Rathod practices at Dolphin Derma Care in Sitapura and "
            "Arya Skin and Hair Clinic in Chaksu, Jaipur."
        )
        home.save()

    Site.objects.filter(is_default_site=True).update(
        site_name="Dr. Naresh Rathod Website"
    )


class Migration(migrations.Migration):
    dependencies = [("website", "0002_seed_site")]

    operations = [
        migrations.RenameField(
            model_name="sitesettings",
            old_name="brand_name",
            new_name="site_title",
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="site_title",
            field=models.CharField(
                default="Dr. Naresh Rathod - Dermatologist", max_length=140
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="professional_title",
            field=models.CharField(
                default="Dermatologist and Cosmetologist", max_length=120
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="location_summary",
            field=models.CharField(
                default=(
                    "Dolphin Derma Care - Sitapura | "
                    "Arya Skin and Hair Clinic - Chaksu | Jaipur"
                ),
                help_text=(
                    "A short display summary, not a substitute for clinic addresses."
                ),
                max_length=255,
            ),
        ),
        migrations.RunPython(reframe_site_identity, migrations.RunPython.noop),
    ]
