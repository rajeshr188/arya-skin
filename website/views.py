from django.db import DatabaseError, connection
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from wagtail.models import Site


@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        response = JsonResponse({"status": "unavailable"}, status=503)
    else:
        response = JsonResponse({"status": "ok"})
    response.headers["Cache-Control"] = "no-store"
    return response


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
