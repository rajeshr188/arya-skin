from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from wagtail.models import Site


@require_GET
@cache_page(3600)
def robots_txt(request):
    site = Site.find_for_request(request) or Site.objects.filter(
        is_default_site=True
    ).first()
    root_url = site.root_url.rstrip("/") if site else request.build_absolute_uri("/").rstrip("/")
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cms/",
        "Disallow: /appointments/",
        "Disallow: /documents/",
        "",
        f"Sitemap: {root_url}{reverse('sitemap')}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
