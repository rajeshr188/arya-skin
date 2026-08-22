import json
import re
from datetime import time

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site

from blog.models import BlogAuthor, BlogIndexPage, BlogPage, BlogSource
from clinics.models import ClinicIndexPage, ClinicOpeningHours, ClinicPage
from doctors.models import DoctorPage


def structured_payload(response):
    match = re.search(
        rb'<script type="application/ld\+json">(.*?)</script>',
        response.content,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError("No JSON-LD payload found")
    return json.loads(match.group(1))


def graph_item(payload, item_type):
    return next(item for item in payload["@graph"] if item["@type"] == item_type)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class TechnicalSEOTests(TestCase):
    def setUp(self):
        cache.clear()
        self.site = Site.objects.get(is_default_site=True)

    def publish_clinic(self, clinic):
        clinic_index = ClinicIndexPage.objects.get()
        if not clinic_index.live:
            clinic_index.save_revision().publish()
        clinic.save_revision().publish()
        clinic.refresh_from_db()
        return clinic

    def create_published_article(self):
        index = BlogIndexPage.objects.get()
        index.save_revision().publish()
        author = BlogAuthor.objects.create(
            name="SEO Test Author",
            role="Test health writer",
        )
        reviewer = BlogAuthor.objects.create(
            name="SEO Test Reviewer",
            role="Test medical reviewer",
        )
        article = BlogPage(
            title="SEO metadata test article",
            slug="seo-metadata-test-article",
            excerpt="Page-specific article description used by the SEO test.",
            body=[("rich_text", "<p>Reviewed automated-test article body.</p>")],
            author=author,
            review_status=BlogPage.ReviewStatus.REVIEWED,
            reviewed_by=reviewer,
            reviewed_on=timezone.localdate(),
            live=False,
            has_unpublished_changes=True,
        )
        index.add_child(instance=article)
        BlogSource.objects.create(
            page=article,
            title="SEO test source",
            url="https://example.com/seo-source",
        )
        article.save_revision().publish()
        article.refresh_from_db()
        return article

    def test_homepage_has_central_metadata_and_factual_schema(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="robots" content="index,follow">')
        self.assertContains(response, '<link rel="canonical" href="http://localhost/">')
        self.assertContains(response, '<meta property="og:type" content="website">')
        self.assertContains(response, '<meta name="twitter:card" content="summary">')

        payload = structured_payload(response)
        website = graph_item(payload, "WebSite")
        person = graph_item(payload, "Person")
        breadcrumbs = graph_item(payload, "BreadcrumbList")
        self.assertEqual(website["url"], "http://localhost/")
        self.assertEqual(person["name"], "Dr. Naresh Rathod")
        self.assertEqual(person["jobTitle"], "Dermatologist and Cosmetologist")
        self.assertEqual(breadcrumbs["itemListElement"][0]["item"], "http://localhost/")

    def test_production_site_configuration_drives_canonical_robots_and_sitemap(self):
        self.site.hostname = "www.example-clinic.test"
        self.site.port = 443
        self.site.save()
        cache.clear()
        doctor = DoctorPage.objects.get()
        doctor.save_revision().publish()

        homepage = self.client.get("/")
        robots = self.client.get(reverse("robots_txt"))
        sitemap = self.client.get(reverse("sitemap"))

        self.assertContains(
            homepage,
            '<link rel="canonical" href="https://www.example-clinic.test/">',
        )
        self.assertContains(
            robots,
            "Sitemap: https://www.example-clinic.test/sitemap.xml",
        )
        self.assertContains(sitemap, "https://www.example-clinic.test/")
        self.assertContains(
            sitemap,
            "https://www.example-clinic.test/dr-naresh-rathod/",
        )

    def test_robots_policy_excludes_operational_and_staff_routes(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        for route in ("/admin/", "/cms/", "/appointments/", "/documents/"):
            self.assertContains(response, f"Disallow: {route}")
        self.assertEqual(self.client.post(reverse("robots_txt")).status_code, 405)

    def test_clinic_schema_uses_only_publicly_enabled_or_populated_facts(self):
        clinic = self.publish_clinic(ClinicPage.objects.get(slug="sitapura"))

        private_payload = structured_payload(self.client.get("/clinics/sitapura/"))
        private_clinic = graph_item(private_payload, "MedicalClinic")
        self.assertEqual(private_clinic["name"], "Dolphin Derma Care")
        self.assertEqual(private_clinic["address"]["addressLocality"], "Sitapura")
        self.assertNotIn("telephone", private_clinic)
        self.assertNotIn("geo", private_clinic)
        self.assertNotIn("hasMap", private_clinic)
        self.assertNotIn("openingHoursSpecification", private_clinic)

        clinic.phone_is_public = True
        clinic.google_maps_url = "https://maps.example.test/verified-location"
        clinic.latitude = "26.750000"
        clinic.longitude = "75.850000"
        ClinicOpeningHours.objects.create(
            page=clinic,
            day="monday",
            opens_at=time(10, 0),
            closes_at=time(14, 0),
        )
        clinic.save_revision().publish()

        public_payload = structured_payload(self.client.get("/clinics/sitapura/"))
        public_clinic = graph_item(public_payload, "MedicalClinic")
        self.assertEqual(public_clinic["telephone"], "9461289316")
        self.assertEqual(public_clinic["geo"]["latitude"], "26.750000")
        self.assertEqual(
            public_clinic["hasMap"],
            "https://maps.example.test/verified-location",
        )
        self.assertEqual(
            public_clinic["openingHoursSpecification"][0]["opens"],
            "10:00",
        )

    def test_doctor_schema_contains_only_structured_published_profile_facts(self):
        doctor = DoctorPage.objects.get()
        doctor.save_revision().publish()

        payload = structured_payload(self.client.get("/dr-naresh-rathod/"))
        person = graph_item(payload, "Person")

        self.assertEqual(person["name"], "Dr. Naresh Rathod")
        self.assertEqual(person["knowsLanguage"], ["Hindi", "English", "Marwari"])
        self.assertNotIn("award", person)

    def test_article_metadata_and_schema_use_article_editorial_records(self):
        article = self.create_published_article()

        response = self.client.get("/blog/seo-metadata-test-article/")
        payload = structured_payload(response)
        posting = graph_item(payload, "BlogPosting")

        self.assertContains(
            response,
            '<meta name="description" content="Page-specific article description used by the SEO test.">',
        )
        self.assertContains(response, '<meta property="og:type" content="article">')
        self.assertContains(response, 'property="article:published_time"')
        self.assertEqual(posting["headline"], article.title)
        self.assertEqual(posting["author"]["name"], "SEO Test Author")
        self.assertEqual(posting["reviewedBy"]["name"], "SEO Test Reviewer")
        self.assertEqual(posting["citation"], ["https://example.com/seo-source"])

    def test_sitemap_and_metadata_exclude_drafts_and_operational_forms(self):
        draft_doctor = DoctorPage.objects.get()
        sitemap = self.client.get(reverse("sitemap"))
        missing = self.client.get("/not-a-real-page/")

        self.assertNotContains(sitemap, "/dr-naresh-rathod/")
        self.assertFalse(draft_doctor.live)
        self.assertEqual(missing.status_code, 404)
        self.assertContains(
            missing,
            '<meta name="robots" content="noindex,nofollow">',
            status_code=404,
        )
        self.assertNotContains(
            missing,
            'type="application/ld+json"',
            status_code=404,
        )

        clinic = self.publish_clinic(ClinicPage.objects.get(slug="sitapura"))
        appointment = self.client.get(reverse("appointments:request"))
        self.assertContains(
            appointment,
            '<meta name="robots" content="noindex,nofollow">',
        )
        self.assertEqual(appointment["X-Robots-Tag"], "noindex, nofollow")
        self.assertNotContains(sitemap, "/appointments/")
        self.assertTrue(clinic.live)

    def test_wagtail_redirect_preserves_a_removed_url_without_seeding_one(self):
        Redirect.add_redirect(
            old_path="/old-clinic-information/",
            redirect_to=self.site.root_page,
            site=self.site,
            is_permanent=True,
        )

        response = self.client.get("/old-clinic-information/")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/")
