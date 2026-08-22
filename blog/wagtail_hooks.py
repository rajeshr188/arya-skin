from django.contrib import messages
from django.shortcuts import redirect
from wagtail import hooks

from .models import BlogPage


@hooks.register("before_publish_page")
def prevent_unreviewed_medical_article_publication(request, page):
    article = page.specific
    if not isinstance(article, BlogPage):
        return None
    errors = article.publication_errors()
    if not errors:
        return None
    messages.error(
        request,
        "This article remains a draft. Complete: " + ", ".join(errors) + ".",
    )
    return redirect("wagtailadmin_pages:edit", article.pk)
