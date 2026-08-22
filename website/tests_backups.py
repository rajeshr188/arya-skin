import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from django.test import SimpleTestCase

from scripts.r2_backup import (
    BackupError,
    backup_configuration,
    download_latest_backup,
    upload_backup,
)


class FakePaginator:
    def __init__(self, client):
        self.client = client

    def paginate(self, **kwargs):
        prefix = kwargs["Prefix"]
        contents = [
            {
                "Key": key,
                "LastModified": value["LastModified"],
            }
            for key, value in self.client.objects.items()
            if key.startswith(prefix)
        ]
        return [{"Contents": contents}]


class FakeR2Client:
    def __init__(self, now):
        self.now = now
        self.objects = {}
        self.deleted = []

    def get_paginator(self, name):
        assert name == "list_objects_v2"
        return FakePaginator(self)

    def upload_file(self, filename, bucket, key, ExtraArgs):
        self.objects[key] = {
            "Body": Path(filename).read_bytes(),
            "Metadata": ExtraArgs["Metadata"],
            "LastModified": self.now,
        }

    def head_object(self, Bucket, Key):
        item = self.objects[Key]
        return {
            "ContentLength": len(item["Body"]),
            "Metadata": item["Metadata"],
        }

    def download_file(self, bucket, key, filename):
        Path(filename).write_bytes(self.objects[key]["Body"])

    def delete_object(self, Bucket, Key):
        self.deleted.append(Key)
        del self.objects[Key]


class R2BackupTests(SimpleTestCase):
    def test_configuration_is_scoped_and_strict(self):
        environment = {
            "R2_BACKUP_ACCESS_KEY_ID": "access",
            "R2_BACKUP_SECRET_ACCESS_KEY": "secret",
            "R2_BACKUP_BUCKET_NAME": "arya-skin-production-backups",
            "R2_BACKUP_ENDPOINT_URL": "https://account.r2.cloudflarestorage.com/",
            "R2_BACKUP_RETENTION_DAYS": "14",
        }
        configuration = backup_configuration(environment)
        self.assertEqual(
            configuration["bucket_name"], "arya-skin-production-backups"
        )
        self.assertEqual(configuration["retention_days"], 14)
        self.assertEqual(
            configuration["endpoint_url"],
            "https://account.r2.cloudflarestorage.com",
        )

        for name, value in (
            ("R2_BACKUP_BUCKET_NAME", "Invalid_Bucket"),
            ("R2_BACKUP_ENDPOINT_URL", "http://account.example.com"),
            ("R2_BACKUP_RETENTION_DAYS", "0"),
            ("R2_BACKUP_RETENTION_DAYS", "forever"),
        ):
            with self.subTest(name=name):
                with self.assertRaises(BackupError):
                    backup_configuration({**environment, name: value})

    def test_encrypted_backup_upload_download_verification_and_retention(self):
        now = datetime(2026, 8, 22, 12, tzinfo=UTC)
        client = FakeR2Client(now)
        old_key = "encrypted/arya-skin-staging-20260701T000000Z.backup.tar.age"
        client.objects[old_key] = {
            "Body": b"old encrypted backup",
            "Metadata": {"sha256": "old"},
            "LastModified": now - timedelta(days=30),
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            backup = directory / "arya-skin-staging-20260822T120000Z.backup.tar.age"
            backup.write_bytes(b"authenticated encrypted backup")
            result = upload_backup(client, "backup-bucket", backup, 14, now=now)

            self.assertEqual(result["deleted"], 1)
            self.assertEqual(client.deleted, [old_key])
            self.assertIn(result["key"], client.objects)

            downloaded = directory / "downloaded.backup.tar.age"
            download_result = download_latest_backup(
                client, "backup-bucket", downloaded
            )
            self.assertEqual(download_result["key"], result["key"])
            self.assertEqual(downloaded.read_bytes(), backup.read_bytes())

    def test_download_rejects_checksum_mismatch_and_removes_temporary_file(self):
        now = datetime(2026, 8, 22, 12, tzinfo=UTC)
        client = FakeR2Client(now)
        key = "encrypted/arya-skin-production-20260822T120000Z.backup.tar.age"
        client.objects[key] = {
            "Body": b"tampered",
            "Metadata": {"sha256": "0" * 64},
            "LastModified": now,
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "download.age"
            with self.assertRaisesMessage(BackupError, "checksum"):
                download_latest_backup(client, "backup-bucket", output)
            self.assertFalse(output.exists())
            self.assertFalse(
                (output.parent / f".{output.name}.temporary").exists()
            )
