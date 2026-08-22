import base64
import binascii

from django.conf import settings
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare


class StagingAccessMiddleware:
    """Protect staging content and prevent all staging responses being indexed."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            settings.IS_STAGING
            and request.path != settings.HEALTH_CHECK_PATH
            and not self._has_valid_credentials(request)
        ):
            response = HttpResponse("Authentication required.", status=401)
            response.headers["WWW-Authenticate"] = (
                f'Basic realm="{settings.STAGING_ACCESS_REALM}"'
            )
            response.headers["Cache-Control"] = "no-store"
        else:
            response = self.get_response(request)

        if settings.SITE_NOINDEX:
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    @staticmethod
    def _has_valid_credentials(request):
        authorization = request.headers.get("Authorization", "")
        scheme, _, encoded = authorization.partition(" ")
        if scheme.lower() != "basic" or not encoded:
            return False
        try:
            decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return False
        username, separator, password = decoded.partition(":")
        return bool(
            separator
            and constant_time_compare(username, settings.STAGING_ACCESS_USERNAME)
            and constant_time_compare(password, settings.STAGING_ACCESS_PASSWORD)
        )
