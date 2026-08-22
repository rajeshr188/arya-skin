import argparse
import hashlib
import os
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.config import Config


BUCKET_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
BACKUP_NAME_PATTERN = re.compile(
    r"^arya-skin-(?:staging|production)-\d{8}T\d{6}Z\.backup\.tar\.age$"
)
OBJECT_PREFIX = "encrypted/"


class BackupError(RuntimeError):
    pass


def backup_configuration(environ):
    variable_names = (
        "R2_BACKUP_ACCESS_KEY_ID",
        "R2_BACKUP_SECRET_ACCESS_KEY",
        "R2_BACKUP_BUCKET_NAME",
        "R2_BACKUP_ENDPOINT_URL",
        "R2_BACKUP_RETENTION_DAYS",
    )
    values = {name: environ.get(name, "").strip() for name in variable_names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise BackupError("Missing backup settings: " + ", ".join(missing))

    bucket_name = values["R2_BACKUP_BUCKET_NAME"]
    if not BUCKET_NAME_PATTERN.fullmatch(bucket_name) or ".." in bucket_name:
        raise BackupError("R2_BACKUP_BUCKET_NAME is invalid.")

    endpoint_url = values["R2_BACKUP_ENDPOINT_URL"].rstrip("/")
    endpoint = urlparse(endpoint_url)
    if (
        endpoint.scheme != "https"
        or not endpoint.hostname
        or endpoint.path
        or endpoint.params
        or endpoint.query
        or endpoint.fragment
    ):
        raise BackupError("R2_BACKUP_ENDPOINT_URL must be an HTTPS endpoint.")

    try:
        retention_days = int(values["R2_BACKUP_RETENTION_DAYS"])
    except ValueError as error:
        raise BackupError("R2_BACKUP_RETENTION_DAYS must be an integer.") from error
    if not 1 <= retention_days <= 90:
        raise BackupError("R2_BACKUP_RETENTION_DAYS must be between 1 and 90.")

    return {
        "access_key": values["R2_BACKUP_ACCESS_KEY_ID"],
        "secret_key": values["R2_BACKUP_SECRET_ACCESS_KEY"],
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "retention_days": retention_days,
    }


def create_client(configuration):
    return boto3.client(
        "s3",
        endpoint_url=configuration["endpoint_url"],
        aws_access_key_id=configuration["access_key"],
        aws_secret_access_key=configuration["secret_key"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as backup_file:
        for chunk in iter(lambda: backup_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_backup_objects(client, bucket_name):
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=OBJECT_PREFIX):
        for item in page.get("Contents", []):
            key = item.get("Key", "")
            if BACKUP_NAME_PATTERN.fullmatch(key.removeprefix(OBJECT_PREFIX)):
                yield item


def upload_backup(client, bucket_name, path, retention_days, now=None):
    path = Path(path).resolve()
    if not path.is_file() or not BACKUP_NAME_PATTERN.fullmatch(path.name):
        raise BackupError("Backup must be a valid, non-empty .backup.tar.age file.")
    size = path.stat().st_size
    if size == 0:
        raise BackupError("Backup must be a valid, non-empty .backup.tar.age file.")

    digest = sha256_file(path)
    key = OBJECT_PREFIX + path.name
    client.upload_file(
        str(path),
        bucket_name,
        key,
        ExtraArgs={
            "ContentType": "application/octet-stream",
            "CacheControl": "no-store",
            "Metadata": {"sha256": digest},
        },
    )
    metadata = client.head_object(Bucket=bucket_name, Key=key)
    if metadata.get("ContentLength") != size:
        raise BackupError("Uploaded backup size verification failed.")
    if metadata.get("Metadata", {}).get("sha256") != digest:
        raise BackupError("Uploaded backup checksum metadata verification failed.")

    cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
    deleted = 0
    for item in iter_backup_objects(client, bucket_name):
        item_key = item["Key"]
        modified = item.get("LastModified")
        if item_key != key and modified and modified < cutoff:
            client.delete_object(Bucket=bucket_name, Key=item_key)
            deleted += 1

    return {"key": key, "size": size, "sha256": digest, "deleted": deleted}


def download_latest_backup(client, bucket_name, output_path):
    objects = list(iter_backup_objects(client, bucket_name))
    if not objects:
        raise BackupError("No encrypted backup objects were found.")
    latest = max(objects, key=lambda item: (item["LastModified"], item["Key"]))
    key = latest["Key"]

    output_path = Path(output_path).resolve()
    if output_path.exists():
        raise BackupError(f"Refusing to overwrite download target: {output_path}")
    if not output_path.parent.is_dir():
        raise BackupError(f"Download directory does not exist: {output_path.parent}")
    temporary_path = output_path.with_name(f".{output_path.name}.temporary")
    if temporary_path.exists():
        raise BackupError(f"Temporary download path already exists: {temporary_path}")

    metadata = client.head_object(Bucket=bucket_name, Key=key)
    expected_size = metadata.get("ContentLength")
    expected_digest = metadata.get("Metadata", {}).get("sha256")
    if not expected_size or not expected_digest:
        raise BackupError("Latest backup lacks required verification metadata.")

    try:
        client.download_file(bucket_name, key, str(temporary_path))
        if temporary_path.stat().st_size != expected_size:
            raise BackupError("Downloaded backup size verification failed.")
        if sha256_file(temporary_path) != expected_digest:
            raise BackupError("Downloaded backup checksum verification failed.")
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return {"key": key, "size": expected_size, "sha256": expected_digest}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Upload or retrieve client-side encrypted Arya Skin backups."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--file", required=True)
    download_parser = subparsers.add_parser("download-latest")
    download_parser.add_argument("--output", required=True)
    return parser


def main():
    arguments = build_parser().parse_args()
    configuration = backup_configuration(os.environ)
    client = create_client(configuration)
    if arguments.command == "upload":
        result = upload_backup(
            client,
            configuration["bucket_name"],
            arguments.file,
            configuration["retention_days"],
        )
        print(f"uploaded_key={result['key']}")
        print(f"uploaded_bytes={result['size']}")
        print(f"expired_objects_deleted={result['deleted']}")
    else:
        result = download_latest_backup(
            client,
            configuration["bucket_name"],
            arguments.output,
        )
        print(f"downloaded_key={result['key']}")
        print(f"downloaded_bytes={result['size']}")


if __name__ == "__main__":
    try:
        main()
    except BackupError as error:
        raise SystemExit(f"backup error: {error}") from error
