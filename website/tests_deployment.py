import base64
import json
import logging
import sys
from types import SimpleNamespace
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse

from django_project.environment import env_bool, postgres_config_from_url
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

    def test_health_check_reports_database_readiness_without_cache(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response.headers["Cache-Control"], "no-store")

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
