"""Secure upload helpers shared by media-bearing models."""

import uuid
from pathlib import Path

from django.core.exceptions import ValidationError

# ImageField already runs Pillow to reject non-images; this adds an extension
# whitelist and size ceiling on top.
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_image(f):
    """Reject uploads that are too large or not an allowed image type."""
    if f is None:
        return f
    if f.size > MAX_IMAGE_BYTES:
        raise ValidationError("Image too large (max 5 MB).")
    if Path(f.name).suffix.lower() not in ALLOWED_IMAGE_EXTS:
        raise ValidationError("Unsupported image type.")
    return f


# Named (not closure) so migrations can serialize it. Random UUID name discards
# the client filename to block path traversal, overwrites, and name leakage.
def _random_path(subdir, filename):
    ext = Path(filename).suffix.lower()
    return f"{subdir}/{uuid.uuid4().hex}{ext}"


def post_image_path(instance, filename):
    return _random_path("posts", filename)


def avatar_path(instance, filename):
    return _random_path("avatars", filename)


ALLOWED_PDF_EXTS = {".pdf"}
MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


def validate_pdf(f):
    """Reject uploads that are too large or not a PDF."""
    if f is None:
        return f
    if f.size > MAX_PDF_BYTES:
        raise ValidationError("PDF too large (max 20 MB).")
    if Path(f.name).suffix.lower() not in ALLOWED_PDF_EXTS:
        raise ValidationError("Unsupported file type (PDF only).")
    return f


def toolkit_pdf_path(instance, filename):
    return _random_path("toolkits", filename)


def toolkit_preview_path(instance, filename):
    return _random_path("toolkit_previews", filename)
