from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


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
