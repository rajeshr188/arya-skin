from django.db import migrations


def seed_blog_index(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page

    BlogIndexPage = apps.get_model("blog", "BlogIndexPage")
    HomePage = apps.get_model("website", "HomePage")

    home_record = HomePage.objects.first()
    if not home_record:
        return

    home_record.blog_section_heading = "Patient education"
    home_record.save()

    if BlogIndexPage.objects.exists():
        return

    home = Page.objects.get(pk=home_record.pk)
    content_type = ContentType.objects.get_or_create(
        app_label="blog", model="blogindexpage"
    )[0]
    page = BlogIndexPage(
        title="Articles",
        slug="blog",
        show_in_menus=True,
        live=False,
        has_unpublished_changes=True,
        content_type_id=content_type.pk,
        locale_id=home.locale_id,
        url_path=f"{home.url_path}blog/",
    )
    home.add_child(instance=page)


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0001_initial"),
        ("website", "0006_homepage_blog_section_heading"),
    ]

    operations = [
        migrations.RunPython(seed_blog_index, migrations.RunPython.noop),
    ]
