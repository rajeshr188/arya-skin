from django.db import migrations


def seed_site(apps, schema_editor):
    """Replace Wagtail's generated welcome page with the verified site identity."""
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page, Site

    HomePage = apps.get_model("website", "HomePage")
    SiteSettings = apps.get_model("website", "SiteSettings")

    if HomePage.objects.exists():
        return

    root = Page.get_first_root_node()
    generated_site = Site.objects.filter(is_default_site=True).first()
    generated_welcome_page = generated_site.root_page if generated_site else None

    home = HomePage(
        title="Arya Skin Clinic",
        # Wagtail's generated welcome page already occupies the sibling slug
        # "home" until it is safely removed after the Site points here.
        slug="arya-skin-clinic",
        seo_title="Arya Skin Clinic | Dr. Naresh Rathod, Dermatologist in Jaipur",
        search_description=(
            "Arya Skin Clinic and Dr. Naresh Rathod, dermatologist, serving "
            "Pratap Nagar and Chaksu in Jaipur."
        ),
        content_type_id=ContentType.objects.get_or_create(
            app_label="website", model="homepage"
        )[0].pk,
        locale_id=root.locale_id,
        url_path="/",
    )
    root.add_child(instance=home)

    if generated_site:
        generated_site.root_page_id = home.pk
        generated_site.site_name = "Arya Skin Clinic"
        generated_site.save(update_fields=["root_page", "site_name"])
        site = generated_site
    else:
        site = Site.objects.create(
            hostname="localhost",
            root_page_id=home.pk,
            site_name="Arya Skin Clinic",
            is_default_site=True,
        )

    SiteSettings.objects.get_or_create(site_id=site.pk)

    # The generated welcome page is left outside the configured Site root. It is
    # unreachable publicly; deleting pages from an early data migration would
    # make Django inspect project page tables that do not exist yet on a clean DB.


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailsearch", "0010_add_text_fields"),
        ("website", "0001_initial"),
    ]

    operations = [migrations.RunPython(seed_site, migrations.RunPython.noop)]
