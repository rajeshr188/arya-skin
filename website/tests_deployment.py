import base64
import json
import logging
import sys
import tempfile
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from django.views.defaults import server_error

from django_project.environment import (
    env_bool,
    postgres_config_from_url,
    r2_media_storage_options,
)
from django_project.logging import JsonFormatter


class DeploymentConfigurationTests(TestCase):
    def test_boolean_environment_values_are_strictly_validated(self):
        self.assertTrue(env_bool({"FEATURE": "yes"}, "FEATURE"))
        self.assertFalse(env_bool({"FEATURE": "off"}, "FEATURE", True))
        with self.assertRaises(ImproperlyConfigured):
            env_bool({"FEATURE": "release"}, "FEATURE")

    def test_postgres_url_is_parsed_with_persistent_health_checked_connections(self):
        config = postgres_config_from_url(
            "postgresql://clinic:p%40ss@database.internal:5433/arya_skin"
            "?sslmode=require&application_name=ignored",
            conn_max_age=120,
        )

        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["NAME"], "arya_skin")
        self.assertEqual(config["USER"], "clinic")
        self.assertEqual(config["PASSWORD"], "p@ss")
        self.assertEqual(config["HOST"], "database.internal")
        self.assertEqual(config["PORT"], "5433")
        self.assertEqual(config["CONN_MAX_AGE"], 120)
        self.assertTrue(config["CONN_HEALTH_CHECKS"])
        self.assertEqual(config["OPTIONS"], {"sslmode": "require"})

    def test_non_postgres_or_incomplete_database_urls_are_rejected(self):
        for database_url in (
            "mysql://user:password@db/name",
            "postgresql://db-without-user/name",
            "postgresql://user@db-without-name",
            "postgresql://user@database:not-a-port/name",
        ):
            with self.subTest(database_url=database_url):
                with self.assertRaises(ImproperlyConfigured):
                    postgres_config_from_url(database_url)

    def test_r2_media_is_optional_outside_production(self):
        self.assertIsNone(r2_media_storage_options({}))
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "USE_R2_MEDIA must be enabled for production",
        ):
            r2_media_storage_options({}, required=True)

    def test_r2_media_configuration_is_bucket_scoped_and_publicly_addressed(self):
        options = r2_media_storage_options(
            {
                "USE_R2_MEDIA": "true",
                "R2_MEDIA_ACCESS_KEY_ID": "bucket-access-key",
                "R2_MEDIA_SECRET_ACCESS_KEY": "bucket-secret-key",
                "R2_MEDIA_BUCKET_NAME": "arya-skin-production-media",
                "R2_MEDIA_ENDPOINT_URL": (
                    "https://account-id.r2.cloudflarestorage.com/"
                ),
                "R2_MEDIA_CUSTOM_DOMAIN": "media.drnareshrathod.com",
            },
            required=True,
        )

        self.assertEqual(options["bucket_name"], "arya-skin-production-media")
        self.assertEqual(
            options["endpoint_url"],
            "https://account-id.r2.cloudflarestorage.com",
        )
        self.assertEqual(options["region_name"], "auto")
        self.assertEqual(options["custom_domain"], "media.drnareshrathod.com")
        self.assertFalse(options["querystring_auth"])
        self.assertIsNone(options["default_acl"])
        self.assertFalse(options["file_overwrite"])

    def test_r2_media_configuration_rejects_missing_or_unsafe_values(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "R2_MEDIA_SECRET_ACCESS_KEY",
        ):
            r2_media_storage_options(
                {
                    "USE_R2_MEDIA": "true",
                    "R2_MEDIA_ACCESS_KEY_ID": "key",
                }
            )

        base_environment = {
            "USE_R2_MEDIA": "true",
            "R2_MEDIA_ACCESS_KEY_ID": "key",
            "R2_MEDIA_SECRET_ACCESS_KEY": "secret",
            "R2_MEDIA_BUCKET_NAME": "arya-skin-production-media",
            "R2_MEDIA_ENDPOINT_URL": (
                "https://account-id.r2.cloudflarestorage.com"
            ),
            "R2_MEDIA_CUSTOM_DOMAIN": "media.drnareshrathod.com",
        }
        invalid_values = (
            ("R2_MEDIA_BUCKET_NAME", "Invalid_Bucket"),
            ("R2_MEDIA_ENDPOINT_URL", "http://account-id.example.com"),
            ("R2_MEDIA_CUSTOM_DOMAIN", "https://media.example.com/path"),
            ("R2_MEDIA_CUSTOM_DOMAIN", "media domain.example.com"),
            ("R2_MEDIA_CUSTOM_DOMAIN", "MEDIA.example.com"),
        )
        for name, value in invalid_values:
            with self.subTest(name=name):
                environment = {**base_environment, name: value}
                with self.assertRaises(ImproperlyConfigured):
                    r2_media_storage_options(environment)

    @override_settings(
        R2_MEDIA_STORAGE_OPTIONS={"bucket_name": "test-production-media"},
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.InMemoryStorage",
            }
        },
    )
    def test_media_migration_dry_run_copy_and_idempotent_rerun(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            image = source / "original_images" / "portrait.jpg"
            image.parent.mkdir()
            image.write_bytes(b"approved portrait")

            dry_run_output = StringIO()
            call_command(
                "migrate_media_to_storage",
                source=str(source),
                dry_run=True,
                stdout=dry_run_output,
            )
            self.assertIn("would copy 1 file(s)", dry_run_output.getvalue())
            self.assertFalse(default_storage.exists("original_images/portrait.jpg"))

            copy_output = StringIO()
            call_command(
                "migrate_media_to_storage",
                source=str(source),
                stdout=copy_output,
            )
            self.assertIn("copied 1 file(s)", copy_output.getvalue())
            self.assertEqual(
                default_storage.open("original_images/portrait.jpg").read(),
                b"approved portrait",
            )

            rerun_output = StringIO()
            call_command(
                "migrate_media_to_storage",
                source=str(source),
                stdout=rerun_output,
            )
            self.assertIn("skipped 1 existing file(s)", rerun_output.getvalue())

    @override_settings(
        R2_MEDIA_STORAGE_OPTIONS={"bucket_name": "test-production-media"},
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.InMemoryStorage",
            }
        },
    )
    def test_media_migration_refuses_to_replace_a_different_existing_object(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            image = source / "original_images" / "portrait.jpg"
            image.parent.mkdir()
            image.write_bytes(b"approved portrait")
            default_storage.save(
                "original_images/portrait.jpg",
                ContentFile(b"different"),
            )

            with self.assertRaisesMessage(CommandError, "different size"):
                call_command("migrate_media_to_storage", source=str(source))

    def test_media_migration_requires_r2_storage(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesMessage(CommandError, "R2 media storage"):
                call_command(
                    "migrate_media_to_storage",
                    source=temporary_directory,
                )

    def test_health_check_reports_database_readiness_without_cache(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_server_error_template_does_not_require_request_context(self):
        response = server_error(
            RequestFactory().get("/failed-request/"),
            template_name="500.html",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Something went wrong", response.content)
        self.assertIn(b"noindex,nofollow", response.content)

    def test_retired_service_worker_clears_caches_and_unregisters(self):
        response = self.client.get(reverse("retired_service_worker"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"],
            "application/javascript; charset=utf-8",
        )
        self.assertEqual(
            response.headers["Cache-Control"],
            "no-store, no-cache, must-revalidate",
        )
        self.assertEqual(response.headers["Service-Worker-Allowed"], "/")
        self.assertContains(response, "caches.keys()")
        self.assertContains(response, "self.registration.unregister()")
        self.assertEqual(
            self.client.post(reverse("retired_service_worker")).status_code,
            405,
        )

    def test_health_check_returns_503_without_exposing_database_details(self):
        with patch(
            "website.views.connection.cursor",
            side_effect=DatabaseError("sensitive database detail"),
        ):
            response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertNotContains(
            response,
            "sensitive database detail",
            status_code=503,
        )

    @override_settings(
        IS_STAGING=True,
        SITE_NOINDEX=True,
        STAGING_ACCESS_USERNAME="reviewer",
        STAGING_ACCESS_PASSWORD="staging-password",
        STAGING_ACCESS_REALM="Arya Skin staging",
        SECURE_SSL_REDIRECT=False,
    )
    def test_staging_is_private_and_noindex_while_health_remains_public(self):
        anonymous = self.client.get("/")

        self.assertEqual(anonymous.status_code, 401)
        self.assertEqual(
            anonymous.headers["WWW-Authenticate"],
            'Basic realm="Arya Skin staging"',
        )
        self.assertEqual(
            anonymous.headers["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )
        self.assertEqual(anonymous.headers["Cache-Control"], "no-store")

        health = self.client.get(reverse("health_check"))
        self.assertEqual(health.status_code, 200)
        self.assertEqual(
            health.headers["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )

        credentials = base64.b64encode(
            b"reviewer:staging-password"
        ).decode("ascii")
        authenticated = self.client.get(
            "/",
            HTTP_AUTHORIZATION=f"Basic {credentials}",
        )
        self.assertEqual(authenticated.status_code, 200)
        self.assertEqual(
            authenticated.headers["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )

    @override_settings(
        IS_STAGING=True,
        SITE_NOINDEX=True,
        STAGING_ACCESS_USERNAME="reviewer",
        STAGING_ACCESS_PASSWORD="staging-password",
        STAGING_ACCESS_REALM="Arya Skin staging",
        SECURE_SSL_REDIRECT=False,
        DEBUG=False,
    )
    def test_staging_media_is_private_and_served_from_the_media_root(self):
        credentials = base64.b64encode(
            b"reviewer:staging-password"
        ).decode("ascii")
        with tempfile.TemporaryDirectory() as temporary_directory:
            media_root = Path(temporary_directory)
            image_directory = media_root / "original_images"
            image_directory.mkdir()
            (image_directory / "portrait.png").write_bytes(b"test-image")

            with override_settings(MEDIA_ROOT=media_root):
                anonymous = self.client.get(
                    "/media/original_images/portrait.png"
                )
                authenticated = self.client.get(
                    "/media/original_images/portrait.png",
                    HTTP_AUTHORIZATION=f"Basic {credentials}",
                )
                authenticated_body = b"".join(
                    authenticated.streaming_content
                )

        self.assertEqual(anonymous.status_code, 401)
        self.assertEqual(authenticated.status_code, 200)
        self.assertEqual(authenticated_body, b"test-image")
        self.assertEqual(
            authenticated.headers["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )

    def test_json_logs_include_paths_but_not_query_strings_or_bodies(self):
        request = SimpleNamespace(
            method="POST",
            path="/appointments/request/sitapura/",
            META={"QUERY_STRING": "name=Private"},
            body=b"phone=private",
        )
        record = logging.LogRecord(
            name="django.request",
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg="Request rejected",
            args=(),
            exc_info=None,
        )
        record.request = request
        record.status_code = 400

        payload = json.loads(JsonFormatter().format(record))

        self.assertEqual(payload["path"], "/appointments/request/sitapura/")
        self.assertEqual(payload["method"], "POST")
        self.assertEqual(payload["status_code"], 400)
        serialized = json.dumps(payload)
        self.assertNotIn("Private", serialized)
        self.assertNotIn("phone=private", serialized)

    def test_json_logs_record_exception_type_without_sensitive_exception_text(self):
        try:
            raise ValueError("patient-entered value")
        except ValueError:
            exception_info = sys.exc_info()

        record = logging.LogRecord(
            name="django.request",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Request failed",
            args=(),
            exc_info=exception_info,
        )
        payload = json.loads(JsonFormatter().format(record))

        self.assertEqual(payload["exception_type"], "ValueError")
        self.assertNotIn("patient-entered value", json.dumps(payload))
