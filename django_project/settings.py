import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .environment import env_bool, env_list, postgres_config_from_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "development").strip().lower()
if ENVIRONMENT not in {"development", "staging", "production"}:
    raise ImproperlyConfigured(
        "DJANGO_ENVIRONMENT must be development, staging, or production."
    )
IS_STAGING = ENVIRONMENT == "staging"
IS_PRODUCTION = ENVIRONMENT == "production"

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env_bool(os.environ, "DJANGO_DEBUG", ENVIRONMENT == "development")
if (IS_STAGING or IS_PRODUCTION) and DEBUG:
    raise ImproperlyConfigured(
        "DJANGO_DEBUG must be false in staging and production."
    )

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
DEVELOPMENT_SECRET_KEY = "django-insecure-local-development-only-change-me"
SECRET_KEY = os.environ.get("SECRET_KEY", DEVELOPMENT_SECRET_KEY)
if not DEBUG and SECRET_KEY == DEVELOPMENT_SECRET_KEY:
    raise ImproperlyConfigured("Set a strong SECRET_KEY whenever DJANGO_DEBUG is false.")
if not DEBUG and len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "SECRET_KEY must contain at least 50 characters whenever DJANGO_DEBUG is false."
    )
SECRET_KEY_FALLBACKS = env_list(os.environ, "SECRET_KEY_FALLBACKS")

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
LOCAL_HOSTS = "localhost,0.0.0.0,127.0.0.1,testserver"
ALLOWED_HOSTS = env_list(
    os.environ,
    "ALLOWED_HOSTS",
    LOCAL_HOSTS if ENVIRONMENT == "development" else "",
)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set ALLOWED_HOSTS for staging and production.")
if (IS_STAGING or IS_PRODUCTION) and "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Do not use a wildcard ALLOWED_HOSTS outside development.")

CSRF_TRUSTED_ORIGINS = env_list(
    os.environ,
    "CSRF_TRUSTED_ORIGINS",
    (
        "http://localhost:8000,http://127.0.0.1:8000"
        if ENVIRONMENT == "development"
        else ""
    ),
)
if (IS_STAGING or IS_PRODUCTION) and not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        "Set CSRF_TRUSTED_ORIGINS to the deployment's HTTPS origin."
    )
if (IS_STAGING or IS_PRODUCTION) and any(
    not origin.startswith("https://") for origin in CSRF_TRUSTED_ORIGINS
):
    raise ImproperlyConfigured(
        "Every staging/production CSRF_TRUSTED_ORIGINS value must use HTTPS."
    )

STAGING_ACCESS_USERNAME = os.environ.get("STAGING_ACCESS_USERNAME", "")
STAGING_ACCESS_PASSWORD = os.environ.get("STAGING_ACCESS_PASSWORD", "")
STAGING_ACCESS_REALM = "Arya Skin staging"
if IS_STAGING and not (STAGING_ACCESS_USERNAME and STAGING_ACCESS_PASSWORD):
    raise ImproperlyConfigured(
        "Set STAGING_ACCESS_USERNAME and STAGING_ACCESS_PASSWORD for staging."
    )
if IS_STAGING and (
    ":" in STAGING_ACCESS_USERNAME or len(STAGING_ACCESS_PASSWORD) < 16
):
    raise ImproperlyConfigured(
        "Use a username without ':' and a staging password of at least 16 characters."
    )
SITE_NOINDEX = IS_STAGING or env_bool(os.environ, "SITE_NOINDEX", False)
HEALTH_CHECK_PATH = "/healthz/"


# Application definition
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "allauth",
    "allauth.account",
    "crispy_forms",
    "crispy_bootstrap5",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # Local
    "accounts",
    "appointments",
    "blog",
    "doctors",
    "clinics",
    "treatments",
    "website",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "website.middleware.StagingAccessMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # django-allauth
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(5, "debug_toolbar.middleware.DebugToolbarMiddleware")

# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "django_project.urls"

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "django_project.wsgi.application"

# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {
        "default": postgres_config_from_url(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        )
    }
elif IS_STAGING or IS_PRODUCTION:
    raise ImproperlyConfigured(
        "Set DATABASE_URL to a PostgreSQL connection URL outside development."
    )
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"

# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = "Asia/Kolkata"

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-USE_I18N
USE_I18N = True

# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [BASE_DIR / "locale"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [BASE_DIR / "static"]

# User-uploaded images and documents. Production must replace this local
# filesystem backend with durable object storage; WhiteNoise serves static only.
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")

# https://whitenoise.readthedocs.io/en/latest/django.html
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-crispy-forms
# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "root@localhost")

# django-debug-toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
# https://docs.djangoproject.com/en/dev/ref/settings/#internal-ips
INTERNAL_IPS = ["127.0.0.1"]

# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = "accounts.CustomUser"

# django-allauth config
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "home"

# https://django-allauth.readthedocs.io/en/latest/views.html#logout-account-logout
ACCOUNT_LOGOUT_REDIRECT_URL = "home"

# https://django-allauth.readthedocs.io/en/latest/installation.html?highlight=backends
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_UNIQUE_EMAIL = True

# Wagtail
WAGTAIL_SITE_NAME = "Dr. Naresh Rathod Website"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "").strip()
if not WAGTAILADMIN_BASE_URL:
    if IS_STAGING or IS_PRODUCTION:
        raise ImproperlyConfigured("Set WAGTAILADMIN_BASE_URL outside development.")
    WAGTAILADMIN_BASE_URL = "http://localhost:8000"
if (IS_STAGING or IS_PRODUCTION) and not WAGTAILADMIN_BASE_URL.startswith(
    "https://"
):
    raise ImproperlyConfigured(
        "WAGTAILADMIN_BASE_URL must use HTTPS outside development."
    )

# Search begins with Wagtail's database backend. The site's initial scale does
# not justify operating a separate search service.
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Basic first-party abuse protection for the public appointment form. This is
# deliberately session-based and stores no IP address or fingerprint.
APPOINTMENT_SUBMISSION_LIMIT = int(
    os.environ.get("APPOINTMENT_SUBMISSION_LIMIT", "5")
)
APPOINTMENT_SUBMISSION_WINDOW_SECONDS = int(
    os.environ.get("APPOINTMENT_SUBMISSION_WINDOW_SECONDS", "3600")
)

# Staging/production transport security. Trust X-Forwarded-Proto only when the
# deployment proxy is known to strip the client header and set its own value.
TRUST_X_FORWARDED_PROTO = env_bool(
    os.environ, "TRUST_X_FORWARDED_PROTO", False
)
if TRUST_X_FORWARDED_PROTO:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env_bool(
    os.environ, "SECURE_SSL_REDIRECT", IS_STAGING or IS_PRODUCTION
)
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
SESSION_COOKIE_SECURE = env_bool(
    os.environ, "SESSION_COOKIE_SECURE", IS_STAGING or IS_PRODUCTION
)
CSRF_COOKIE_SECURE = env_bool(
    os.environ, "CSRF_COOKIE_SECURE", IS_STAGING or IS_PRODUCTION
)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = int(
    os.environ.get("SECURE_HSTS_SECONDS", "300" if IS_STAGING else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    os.environ, "SECURE_HSTS_INCLUDE_SUBDOMAINS", False
)
SECURE_HSTS_PRELOAD = env_bool(os.environ, "SECURE_HSTS_PRELOAD", False)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING" if DEBUG else "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "django_project.logging.JsonFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
