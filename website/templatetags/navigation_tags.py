from django import template

from clinics.models import ClinicPage
from website.models import ContactPage, StandardPage


register = template.Library()


@register.simple_tag
def public_contact_page():
    return ContactPage.objects.live().public().first()


@register.simple_tag
def public_footer_clinics():
    return ClinicPage.objects.live().public().order_by("path")


@register.simple_tag
def public_standard_pages():
    return StandardPage.objects.live().public().order_by("path")
