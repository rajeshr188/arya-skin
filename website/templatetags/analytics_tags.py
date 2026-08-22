import re

from django import template
from wagtail.models import Site

from website.models import SiteSettings, StandardPage


register = template.Library()

GA4_ID_PATTERN = re.compile(r"G-[A-Z0-9]+")
GTM_ID_PATTERN = re.compile(r"GTM-[A-Z0-9]+")

PAGE_TYPES = {
    "HomePage": "home",
    "DoctorPage": "doctor",
    "ClinicIndexPage": "clinic_index",
    "ClinicPage": "clinic",
    "TreatmentIndexPage": "treatment_index",
    "TreatmentPage": "treatment",
    "BlogIndexPage": "article_index",
    "BlogPage": "article",
    "ContactPage": "contact",
    "StandardPage": "standard",
}


@register.simple_tag(takes_context=True)
def analytics_context(context):
    request = context["request"]
    page = context.get("page")
    page = page.specific if page else None
    site_settings = SiteSettings.for_request(request)

    ga4_id = site_settings.google_analytics_id.strip().upper()
    gtm_id = site_settings.google_tag_manager_id.strip().upper()
    provider = ""
    tracking_id = ""
    if GA4_ID_PATTERN.fullmatch(ga4_id) and not gtm_id:
        provider = "ga4"
        tracking_id = ga4_id
    elif GTM_ID_PATTERN.fullmatch(gtm_id) and not ga4_id:
        provider = "gtm"
        tracking_id = gtm_id

    page_type = PAGE_TYPES.get(page.__class__.__name__, "other") if page else "other"
    clinic_slug = page.slug if page_type == "clinic" else ""
    treatment_slug = page.slug if page_type == "treatment" else ""
    view_event = {
        "clinic": "clinic_view",
        "treatment": "treatment_view",
    }.get(page_type, "")

    privacy_page = None
    site = getattr(request, "site", None) or Site.find_for_request(request)
    if site_settings.analytics_enabled and site:
        privacy_page = (
            StandardPage.objects.descendant_of(site.root_page)
            .live()
            .public()
            .filter(slug="privacy")
            .first()
        )

    enabled = bool(site_settings.analytics_enabled and provider and privacy_page)

    return {
        "enabled": enabled,
        "config": {"provider": provider, "tracking_id": tracking_id},
        "page_type": page_type,
        "clinic_slug": clinic_slug,
        "treatment_slug": treatment_slug,
        "view_event": view_event,
        "privacy_url": privacy_page.url if privacy_page else "",
        "search_console_verification": (
            site_settings.google_search_console_verification.strip()
        ),
    }
