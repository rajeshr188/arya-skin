import json

from blog.models import BlogPage
from clinics.models import ClinicPage
from doctors.models import DoctorPage
from treatments.models import TreatmentPage
from wagtail.images import get_image_model
from wagtail.models import Page
from website.models import SiteSettings


pages = [
    {
        "type": page.specific_class.__name__ if page.specific_class else "Page",
        "title": page.title,
        "slug": page.slug,
        "live": page.live,
        "in_menu": page.show_in_menus,
        "has_unpublished_changes": page.has_unpublished_changes,
    }
    for page in Page.objects.exclude(depth=1).specific().order_by("path")
]

doctors = [
    {
        "title": page.title,
        "live": page.live,
        "professional_title": page.professional_title,
        "has_portrait": bool(page.portrait_id),
        "has_biography": bool(page.biography),
        "experience_claim_complete": (
            page.experience_years is not None
            and page.experience_as_of_date is not None
        ),
        "qualifications": page.qualifications.count(),
        "registrations": page.registrations.count(),
        "specialties": page.specialties.count(),
        "languages": page.languages.count(),
        "memberships": page.memberships.count(),
        "has_affiliations": bool(page.professional_affiliations),
        "has_philosophy": bool(page.philosophy_of_care),
    }
    for page in DoctorPage.objects.all()
]

clinics = [
    {
        "title": page.title,
        "slug": page.slug,
        "live": page.live,
        "locality": page.locality,
        "has_address": bool(page.address),
        "postal_code": page.postal_code,
        "phone_present": bool(page.phone),
        "phone_public": page.phone_is_public,
        "whatsapp_present": bool(page.whatsapp),
        "whatsapp_public": page.whatsapp_is_public,
        "opening_hours": page.opening_hours.count(),
        "services": page.services.count(),
        "photos": page.gallery_images.count(),
        "has_doctor_availability": bool(page.doctor_availability),
        "has_maps_url": bool(page.google_maps_url),
        "has_business_profile_url": bool(page.google_business_profile_url),
        "has_landmark": bool(page.nearby_landmark),
        "has_parking_information": bool(page.parking_information),
        "has_accessibility_information": bool(page.accessibility_information),
    }
    for page in ClinicPage.objects.all()
]

settings = SiteSettings.objects.first()
social_links = []
if settings:
    social_links = [
        settings.instagram_url,
        settings.facebook_url,
        settings.youtube_url,
        settings.linkedin_url,
    ]

report = {
    "pages": pages,
    "doctors": doctors,
    "clinics": clinics,
    "treatments": {
        "total": TreatmentPage.objects.count(),
        "live": TreatmentPage.objects.live().count(),
    },
    "articles": {
        "total": BlogPage.objects.count(),
        "live": BlogPage.objects.live().count(),
    },
    "images": get_image_model().objects.count(),
    "site_settings": {
        "has_primary_phone": bool(settings and settings.primary_phone),
        "has_default_whatsapp": bool(settings and settings.default_whatsapp),
        "has_email": bool(settings and settings.default_email),
        "social_links": sum(bool(value) for value in social_links),
        "analytics_enabled": bool(settings and settings.analytics_enabled),
        "has_default_social_image": bool(
            settings and settings.default_social_image_id
        ),
    },
}

print(json.dumps(report, indent=2, default=str))
