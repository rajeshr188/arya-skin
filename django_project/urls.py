from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from website.views import (
    health_check,
    local_media_file,
    retired_service_worker,
    robots_txt,
)

urlpatterns = [
    path("healthz/", health_check, name="health_check"),
    path("sw.js", retired_service_worker, name="retired_service_worker"),
    path("media/<path:path>", local_media_file, name="local_media_file"),
    path("admin/", admin.site.urls),
    path("appointments/", include("appointments.urls")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, name="sitemap"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Keep Wagtail last: its page router is the public-site catch-all.
urlpatterns += [path("", include(wagtail_urls))]
