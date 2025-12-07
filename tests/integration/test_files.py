import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from dkc.application.models import Application
from dkc.application.files_upload import MAX_ADVOCACY_UPLOAD_SIZE_BYTES
from common.models import Settings
from datetime import datetime

from google.cloud import ndb


def test_upload_file(client, login, mock_user, ndb_context, settings):

    with patch("dkc.application.files_upload.gcs") as mock_gcs, patch(
        "dkc.application.files_upload.storage"
    ) as mock_storage:

        mock_bucket = MagicMock()
        mock_bucket.name = "test-bucket"
        mock_gcs.get_bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_blob.name = "uploads/2025/test_key/test.pdf"
        mock_blob.size = 1024
        mock_blob.content_type = "application/pdf"
        mock_storage.Blob.return_value = mock_blob

        mock_user.application.get.return_value.key = ndb.Key(Application, "test_app")

        data = {"upload_file": (BytesIO(b"test content"), "test.pdf")}

        response = client.post(
            "/application/upload/activities/advocacy",
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert b"test.pdf" in response.data

        mock_gcs.get_bucket.assert_called_with("test-bucket")
        mock_blob.upload_from_file.assert_called()

        assert mock_user.application.get().put.called
        mock_user.application.get().advocacy_materials.append.assert_called()


def test_upload_file_too_large(client, login, mock_user):
    with patch("dkc.application.files_upload.MAX_ADVOCACY_UPLOAD_SIZE_BYTES", 1):
        data = {"upload_file": (BytesIO(b"too large"), "large.pdf")}
        response = client.post(
            "/application/upload/activities/advocacy",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 413


def test_delete_file(client, login, mock_user, ndb_context):
    from dkc.application.models import GCSObjectReference

    app_key = ndb.Key(Application, "test_app")
    mock_user.application = app_key

    obj_ref = GCSObjectReference(
        parent=app_key,
        bucket_name="b",
        object_name="o",
        filename="f",
        content_type="c",
        bytes_size=1,
    )
    obj_ref_key = obj_ref.put()

    app = Application(key=app_key)
    app.advocacy_materials = [obj_ref_key]
    app.put()

    with patch("dkc.application.files_delete.gcs") as mock_gcs, patch(
        "dkc.application.files_delete.storage"
    ) as mock_storage:

        mock_bucket = MagicMock()
        mock_gcs.get_bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_storage.Blob.return_value = mock_blob

        url = f'/application/delete/f/{obj_ref_key.urlsafe().decode("utf-8")}'
        response = client.post(url)

        assert response.status_code == 204

        mock_blob.delete.assert_called()

        updated_app = app_key.get()
        assert obj_ref_key not in updated_app.advocacy_materials
        assert obj_ref_key.get() is None
