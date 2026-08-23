from django.contrib import messages
from django.shortcuts import redirect
from wagtail import hooks

from .models import BeforeAfterGalleryPage


@hooks.register("before_publish_page")
def prevent_unapproved_gallery_publication(request, page):
    gallery = page.specific
    if not isinstance(gallery, BeforeAfterGalleryPage):
        return None
    errors = gallery.publication_errors()
    if not errors:
        return None
    messages.error(
        request,
        "This gallery remains a draft. Complete: " + ", ".join(errors) + ".",
    )
    return redirect("wagtailadmin_pages:edit", gallery.pk)
