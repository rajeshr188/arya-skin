from django.conf import settings
from django.db import DatabaseError, connection
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.views.static import serve
from wagtail.models import Site


RETIRED_SERVICE_WORKER = """\
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
      .then(() => self.registration.unregister())
      .then(() => self.clients.matchAll({ type: "window" }))
      .then((clients) => Promise.all(
        clients.map((client) => client.navigate(client.url))
      ))
  );
});
"""


@require_GET
def retired_service_worker(request):
    """Remove a service worker left by a site previously hosted on this origin."""
    response = HttpResponse(
        RETIRED_SERVICE_WORKER,
        content_type="application/javascript; charset=utf-8",
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Service-Worker-Allowed"] = "/"
    return response


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
def local_media_file(request, path):
    """Serve persistent local media only in development or private staging."""
    if not (settings.DEBUG or settings.IS_STAGING):
        raise Http404
    return serve(request, path, document_root=settings.MEDIA_ROOT)


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
