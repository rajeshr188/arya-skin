from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Copy a filesystem media tree to the configured production storage."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            required=True,
            help="Read-only source directory containing existing media files.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List and validate work without uploading objects.",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "R2_MEDIA_STORAGE_OPTIONS", None):
            raise CommandError(
                "R2 media storage is not configured; refusing to copy media."
            )

        source = Path(options["source"]).resolve()
        if not source.is_dir():
            raise CommandError(f"Media source is not a directory: {source}")

        files = []
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                self.stderr.write(f"Skipping symbolic link: {path}")
                continue
            if path.is_file():
                files.append(path)

        copied = 0
        skipped = 0
        dry_run = options["dry_run"]

        for path in files:
            object_name = path.relative_to(source).as_posix()
            source_size = path.stat().st_size

            if default_storage.exists(object_name):
                destination_size = default_storage.size(object_name)
                if destination_size != source_size:
                    raise CommandError(
                        f"Existing object has a different size: {object_name} "
                        f"(source {source_size}, destination {destination_size})"
                    )
                skipped += 1
                continue

            if dry_run:
                copied += 1
                continue

            with path.open("rb") as source_file:
                saved_name = default_storage.save(
                    object_name,
                    File(source_file, name=object_name),
                )
            if saved_name != object_name:
                default_storage.delete(saved_name)
                raise CommandError(
                    f"Storage changed object name from {object_name} to {saved_name}."
                )
            if default_storage.size(object_name) != source_size:
                default_storage.delete(object_name)
                raise CommandError(f"Uploaded object size mismatch: {object_name}")
            copied += 1

        action = "would copy" if dry_run else "copied"
        self.stdout.write(
            self.style.SUCCESS(
                f"Media migration {action} {copied} file(s); "
                f"skipped {skipped} existing file(s)."
            )
        )
