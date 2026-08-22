import json

from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

from website.models import SiteSettings


register = template.Library()


def _specific_page(page):
    return page.specific if page else None


def _plain_text(value):
    if not value:
        return ""
    return " ".join(strip_tags(str(value)).split())


def _description_for(page, site_settings):
    candidates = [
        getattr(page, "search_description", ""),
        getattr(page, "excerpt", ""),
        getattr(page, "summary", ""),
        getattr(page, "introduction", ""),
        getattr(page, "biography", ""),
    ]
    for candidate in candidates:
        description = _plain_text(candidate)
        if description:
            return Truncator(description).chars(160)
    return Truncator(
        f"{site_settings.doctor_name}, {site_settings.professional_title}. "
        f"{site_settings.location_summary}"
    ).chars(160)


def _image_for(page, site_settings):
    for attribute in ("featured_image", "portrait"):
        image = getattr(page, attribute, None)
        if image:
            return image
    if page and page.__class__.__name__ == "ClinicPage":
        gallery_item = page.gallery_images.select_related("image").first()
        if gallery_item:
            return gallery_item.image
    return site_settings.default_social_image


def _absolute_image_url(request, image):
    if not image:
        return ""
    rendition = image.get_rendition("fill-1200x630")
    return request.build_absolute_uri(rendition.url)


@register.simple_tag(takes_context=True)
def seo_context(context):
    request = context["request"]
    page = _specific_page(context.get("page"))
    site_settings = SiteSettings.for_request(request)
    canonical = ""
    if page:
        canonical = page.full_url or request.build_absolute_uri(page.url)
    image_url = _absolute_image_url(request, _image_for(page, site_settings))
    return {
        "title": (
            getattr(page, "seo_title", "")
            or getattr(page, "title", "")
            or site_settings.site_title
        ),
        "description": _description_for(page, site_settings),
        "canonical": canonical,
        "image_url": image_url,
        "og_type": "article" if page and page.__class__.__name__ == "BlogPage" else "website",
        "twitter_card": "summary_large_image" if image_url else "summary",
        "robots": "index,follow" if page and page.live else "noindex,nofollow",
        "published_at": getattr(page, "first_published_at", None),
        "modified_at": getattr(page, "last_published_at", None),
    }


def _person_data(person, doctor_id=None):
    data = {"@type": "Person", "name": person.name, "jobTitle": person.role}
    if doctor_id and person.doctor_page_id:
        data["@id"] = doctor_id
    return data


@register.simple_tag(takes_context=True)
def structured_data(context):
    request = context["request"]
    page = _specific_page(context.get("page"))
    if not page or not page.live:
        return ""

    from blog.models import BlogIndexPage, BlogPage
    from clinics.models import ClinicIndexPage, ClinicPage
    from doctors.models import DoctorPage
    from treatments.models import TreatmentIndexPage, TreatmentPage
    from website.models import ContactPage, HomePage, StandardPage

    site_settings = SiteSettings.for_request(request)
    site = page.get_site()
    root_url = site.root_url.rstrip("/")
    canonical = page.full_url or request.build_absolute_uri(page.url)
    description = _description_for(page, site_settings)
    doctor_id = f"{root_url}/#doctor"
    website_id = f"{root_url}/#website"

    graph = [
        {
            "@type": "WebSite",
            "@id": website_id,
            "url": f"{root_url}/",
            "name": site_settings.site_title,
            "publisher": {"@id": doctor_id},
        },
        {
            "@type": "Person",
            "@id": doctor_id,
            "name": site_settings.doctor_name,
            "jobTitle": site_settings.professional_title,
            "url": f"{root_url}/",
        },
    ]

    webpage_type = "WebPage"
    if isinstance(page, (BlogIndexPage, ClinicIndexPage, TreatmentIndexPage)):
        webpage_type = "CollectionPage"
    webpage = {
        "@type": webpage_type,
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": page.seo_title or page.title,
        "description": description,
        "isPartOf": {"@id": website_id},
    }

    if isinstance(page, HomePage):
        graph[1]["url"] = canonical
        webpage["about"] = {"@id": doctor_id}
    elif isinstance(page, DoctorPage):
        graph[1]["url"] = canonical
        languages = list(page.languages.values_list("name", flat=True))
        if languages:
            graph[1]["knowsLanguage"] = languages
        webpage["mainEntity"] = {"@id": doctor_id}
    elif isinstance(page, ClinicPage):
        address = {
            "@type": "PostalAddress",
            "addressLocality": page.locality,
            "addressRegion": page.state,
        }
        if page.address:
            address["streetAddress"] = page.address
        if page.postal_code:
            address["postalCode"] = page.postal_code
        clinic = {
            "@type": "MedicalClinic",
            "@id": f"{canonical}#clinic",
            "name": page.title,
            "url": canonical,
            "address": address,
        }
        if page.phone_uri:
            clinic["telephone"] = page.phone
        if page.google_maps_url:
            clinic["hasMap"] = page.google_maps_url
        if page.latitude is not None and page.longitude is not None:
            clinic["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(page.latitude),
                "longitude": str(page.longitude),
            }
        opening_hours = []
        for entry in page.opening_hours.all():
            if entry.is_closed or not entry.opens_at or not entry.closes_at:
                continue
            opening_hours.append(
                {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": f"https://schema.org/{entry.get_day_display()}",
                    "opens": entry.opens_at.strftime("%H:%M"),
                    "closes": entry.closes_at.strftime("%H:%M"),
                }
            )
        if opening_hours:
            clinic["openingHoursSpecification"] = opening_hours
        graph.append(clinic)
        webpage["mainEntity"] = {"@id": clinic["@id"]}
    elif isinstance(page, BlogPage):
        article = {
            "@type": "BlogPosting",
            "@id": f"{canonical}#article",
            "headline": page.title,
            "description": description,
            "url": canonical,
            "mainEntityOfPage": {"@id": webpage["@id"]},
            "datePublished": page.first_published_at.isoformat(),
            "dateModified": page.last_published_at.isoformat(),
            "author": _person_data(page.author, doctor_id),
            "reviewedBy": _person_data(page.reviewed_by, doctor_id),
            "citation": list(page.sources.values_list("url", flat=True)),
        }
        image_url = _absolute_image_url(
            request, _image_for(page, site_settings)
        )
        if image_url:
            article["image"] = image_url
        graph.append(article)
        webpage["mainEntity"] = {"@id": article["@id"]}
    elif isinstance(page, TreatmentPage):
        webpage["about"] = page.title
    elif isinstance(page, (ContactPage, StandardPage)):
        pass

    graph.append(webpage)

    breadcrumb_items = []
    ancestors = page.get_ancestors(inclusive=True).live().public()
    for ancestor in ancestors:
        if ancestor.depth <= 1:
            continue
        url = ancestor.full_url or request.build_absolute_uri(ancestor.url)
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": len(breadcrumb_items) + 1,
                "name": ancestor.title,
                "item": url,
            }
        )
    if breadcrumb_items:
        graph.append(
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumbs",
                "itemListElement": breadcrumb_items,
            }
        )

    payload = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    payload = payload.replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return mark_safe(payload)
