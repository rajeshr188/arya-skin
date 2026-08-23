from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from wagtail.images import get_image_model


object_name = f"healthchecks/storage-write-{uuid4().hex}.txt"
saved_name = None

try:
    saved_name = default_storage.save(
        object_name,
        ContentFile(b"Arya Skin production media storage write check.\n"),
    )
    if saved_name != object_name:
        raise RuntimeError(f"Storage changed the diagnostic name to {saved_name!r}.")
    if not default_storage.exists(saved_name):
        raise RuntimeError("Diagnostic object was not readable after upload.")
    print("media_storage_write=passed")
finally:
    if saved_name and default_storage.exists(saved_name):
        default_storage.delete(saved_name)

if saved_name and default_storage.exists(saved_name):
    raise RuntimeError("Diagnostic object still exists after cleanup.")

print("media_storage_cleanup=passed")

images = get_image_model().objects.all().only("id", "file")
missing_image_ids = [
    image.id for image in images if not default_storage.exists(image.file.name)
]
print(f"cms_images_checked={images.count()}")
print(f"cms_images_missing={len(missing_image_ids)}")
if missing_image_ids:
    raise RuntimeError(
        f"CMS image records with missing originals: {missing_image_ids!r}"
    )
