from django import template
from wagtail.models import Site

from clinics.models import ClinicPage
from website.models import ContactPage, StandardPage


register = template.Library()


@register.simple_tag(takes_context=True)
def public_menu_pages(context):
    request = context.get("request")
    if request is None:
        return []

    site = Site.find_for_request(request)
    if site is None:
        return []

    contact_page_ids = ContactPage.objects.values_list("pk", flat=True)
    return (
        site.root_page.get_children()
        .live()
        .public()
        .in_menu()
        .exclude(pk__in=contact_page_ids)
    )


@register.simple_tag
def public_contact_page():
    return ContactPage.objects.live().public().first()


@register.simple_tag
def public_footer_clinics():
    return ClinicPage.objects.live().public().order_by("path")


@register.simple_tag
def public_standard_pages():
    return StandardPage.objects.live().public().order_by("path")
