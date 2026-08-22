import re
from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
R2_BUCKET_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
HOSTNAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.IGNORECASE,
)


def env_bool(environ, name, default=False):
    value = environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ImproperlyConfigured(
        f"{name} must be one of: true, false, 1, 0, yes, no, on, off."
    )


def env_list(environ, name, default=""):
    return [item.strip() for item in environ.get(name, default).split(",") if item.strip()]


def r2_media_storage_options(environ, required=False):
    enabled = env_bool(environ, "USE_R2_MEDIA", False)
    if not enabled:
        if required:
            raise ImproperlyConfigured(
                "USE_R2_MEDIA must be enabled for production."
            )
        return None

    variable_names = (
        "R2_MEDIA_ACCESS_KEY_ID",
        "R2_MEDIA_SECRET_ACCESS_KEY",
        "R2_MEDIA_BUCKET_NAME",
        "R2_MEDIA_ENDPOINT_URL",
        "R2_MEDIA_CUSTOM_DOMAIN",
    )
    values = {name: environ.get(name, "").strip() for name in variable_names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ImproperlyConfigured(
            "Missing required R2 media settings: " + ", ".join(missing)
        )

    bucket_name = values["R2_MEDIA_BUCKET_NAME"]
    if not R2_BUCKET_NAME_PATTERN.fullmatch(bucket_name) or ".." in bucket_name:
        raise ImproperlyConfigured(
            "R2_MEDIA_BUCKET_NAME must be a valid lowercase bucket name."
        )

    endpoint_url = values["R2_MEDIA_ENDPOINT_URL"].rstrip("/")
    endpoint = urlparse(endpoint_url)
    if (
        endpoint.scheme != "https"
        or not endpoint.hostname
        or endpoint.path
        or endpoint.params
        or endpoint.query
        or endpoint.fragment
    ):
        raise ImproperlyConfigured(
            "R2_MEDIA_ENDPOINT_URL must be an HTTPS S3 endpoint without a path."
        )

    custom_domain = values["R2_MEDIA_CUSTOM_DOMAIN"].rstrip("/")
    if (
        not HOSTNAME_PATTERN.fullmatch(custom_domain)
        or custom_domain.lower() != custom_domain
    ):
        raise ImproperlyConfigured(
            "R2_MEDIA_CUSTOM_DOMAIN must be a lowercase hostname without a "
            "scheme, port, or path."
        )

    return {
        "access_key": values["R2_MEDIA_ACCESS_KEY_ID"],
        "secret_key": values["R2_MEDIA_SECRET_ACCESS_KEY"],
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "region_name": "auto",
        "custom_domain": custom_domain,
        "querystring_auth": False,
        "default_acl": None,
        "file_overwrite": False,
        "signature_version": "s3v4",
        "object_parameters": {
            "CacheControl": "public, max-age=86400",
        },
    }


def postgres_config_from_url(database_url, conn_max_age=60):
    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured(
            "DATABASE_URL must use the postgres:// or postgresql:// scheme."
        )

    name = unquote(parsed.path.lstrip("/"))
    if not all((name, parsed.hostname, parsed.username)):
        raise ImproperlyConfigured(
            "DATABASE_URL must include a database name, host, and username."
        )

    try:
        port = parsed.port or 5432
    except ValueError as error:
        raise ImproperlyConfigured("DATABASE_URL contains an invalid port.") from error

    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": unquote(parsed.username),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname,
        "PORT": str(port),
        "CONN_MAX_AGE": conn_max_age,
        "CONN_HEALTH_CHECKS": True,
    }

    query = parse_qs(parsed.query)
    allowed_options = {"sslmode", "sslrootcert", "sslcert", "sslkey"}
    options = {
        key: values[-1]
        for key, values in query.items()
        if key in allowed_options and values
    }
    if options:
        config["OPTIONS"] = options
    return config
