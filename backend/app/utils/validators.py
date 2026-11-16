"""
validators.py — Upload validation utilities.
"""

from __future__ import annotations

import os
import uuid

from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


class UploadValidationError(ValueError):
    """Raised when the uploaded file fails validation."""


def validate_upload(file: FileStorage | None) -> None:
    """
    Validate the uploaded file object.

    :raises UploadValidationError: on any validation failure.
    """
    if file is None or file.filename == "":
        raise UploadValidationError("No file was uploaded. Please select a PDF or DOCX resume.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file."
        )

    # Check size (read then seek back so the stream can still be saved)
    file.stream.seek(0, 2)  # seek to end
    size = file.stream.tell()
    file.stream.seek(0)     # rewind

    if size == 0:
        raise UploadValidationError("The uploaded file is empty.")

    if size > MAX_UPLOAD_BYTES:
        mb = size / (1024 * 1024)
        raise UploadValidationError(
            f"File size ({mb:.1f} MB) exceeds the 5 MB limit. "
            "Please compress the file or remove unnecessary pages."
        )


def build_safe_storage_path(upload_folder: str, original_filename: str) -> tuple[str, str]:
    """
    Generate a safe, unique storage filename and return (stored_name, full_path).

    The stored name is a UUID hex + original extension to prevent collisions
    and path-traversal attacks.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(upload_folder, stored_name)
    return stored_name, full_path
