"""Cloud Storage service for uploading generated media assets."""

import os
from typing import Optional

from google.cloud import storage

_client: Optional[storage.Client] = None


def get_storage_client() -> storage.Client:
    global _client
    if _client is None:
        project = os.environ.get("GCP_PROJECT_ID", "dreamscape-hackathon")
        _client = storage.Client(project=project)
    return _client


def get_bucket_name() -> str:
    return os.environ.get("GCS_BUCKET_NAME", "dreamscape-media")


def upload_bytes(
    data: bytes,
    destination_path: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload bytes to Cloud Storage and return the gs:// URI."""
    client = get_storage_client()
    bucket = client.bucket(get_bucket_name())
    blob = bucket.blob(destination_path)
    blob.upload_from_string(data, content_type=content_type)
    return f"gs://{get_bucket_name()}/{destination_path}"


def upload_file(
    local_path: str,
    destination_path: str,
    content_type: Optional[str] = None,
) -> str:
    """Upload a local file to Cloud Storage and return the gs:// URI."""
    client = get_storage_client()
    bucket = client.bucket(get_bucket_name())
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(local_path, content_type=content_type)
    return f"gs://{get_bucket_name()}/{destination_path}"


def get_signed_url(blob_path: str, expiration_minutes: int = 60) -> str:
    """Generate a signed URL for temporary public access."""
    from datetime import timedelta

    client = get_storage_client()
    bucket = client.bucket(get_bucket_name())
    blob = bucket.blob(blob_path)
    url = blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )
    return url


def get_public_url(blob_path: str) -> str:
    """Get the public URL for a blob (bucket must have public access)."""
    return f"https://storage.googleapis.com/{get_bucket_name()}/{blob_path}"


def delete_blob(blob_path: str):
    """Delete a blob from Cloud Storage."""
    client = get_storage_client()
    bucket = client.bucket(get_bucket_name())
    blob = bucket.blob(blob_path)
    blob.delete()
