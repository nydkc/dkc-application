import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from google.cloud import ndb
from dkc.application.models import Application
from dkc.auth.models import User
from dkc.application.files_upload import (
    MAX_ADVOCACY_ITEMS,
    MAX_NEWSLETTER_ITEMS,
    MAX_OTHER_ITEMS,
)
from dkc.application.models import GCSObjectReference

@pytest.fixture
def mock_gcs():
    with patch("dkc.application.files_upload.gcs") as mock_gcs, \
         patch("dkc.application.files_upload.storage") as mock_storage, \
         patch("dkc.application.files_delete.gcs") as mock_delete_gcs, \
         patch("dkc.application.files_delete.storage") as mock_delete_storage:

        mock_bucket = MagicMock()
        mock_bucket.name = "test-bucket"
        mock_gcs.get_bucket.return_value = mock_bucket
        mock_delete_gcs.get_bucket.return_value = mock_bucket

        mock_blob = MagicMock()
        mock_blob.name = "uploads/test-file.pdf"
        mock_blob.size = 1024
        mock_blob.content_type = "application/pdf"

        mock_storage.Blob.return_value = mock_blob
        mock_delete_storage.Blob.return_value = mock_blob

        yield {
            "gcs": mock_gcs,
            "storage": mock_storage,
            "blob": mock_blob,
            "bucket": mock_bucket
        }

@pytest.fixture
def mock_keys():
    with patch("google.cloud.ndb.Key") as mock_key_cls:
        key_instance = MagicMock()
        key_instance.urlsafe.return_value = b"safe_key"
        key_instance.id.return_value = 1
        mock_key_cls.return_value = key_instance
        yield key_instance

@pytest.fixture
def mock_gcs_obj_ref():
    with patch("dkc.application.files_upload.GCSObjectReference") as mock_cls:

        # Setup mock behavior for allocate_ids to return a mock key
        mock_key = MagicMock()
        mock_key.urlsafe.return_value = b"mock_file_key"
        mock_cls.allocate_ids.return_value = [mock_key]

        # Setup mock instance
        mock_instance = MagicMock()
        mock_instance.put.return_value = mock_key
        mock_key.get.return_value = mock_instance  # Fix TypeError: mock_key.get() should return our configured instance
        mock_instance.key = mock_key # Fix JSON serialization (obj_ref.key)

        # Serializable attributes
        mock_instance.filename = "test.pdf"
        mock_instance.content_type = "application/pdf"
        mock_instance.bytes_size = 1024  # Fix TypeError in byteConversion
        mock_instance.bucket_name = "test-bucket"

        mock_cls.return_value = mock_instance

        yield {"cls": mock_cls, "instance": mock_instance, "key": mock_key}

def test_upload_activities_advocacy_success(client, login, mock_user, mock_gcs, mock_gcs_obj_ref):
    # Initialize list
    mock_user.application.get.return_value.advocacy_materials = []

    data = {
        "upload_file": (BytesIO(b"test content"), "test.pdf")
    }
    response = client.post(
        "/application/upload/activities/advocacy",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert b"test.pdf" in response.data

    # Verify saved to application
    saved_app = mock_user.application.get.return_value
    assert len(saved_app.advocacy_materials) == 1
    # Check that what was appended is the key returned by our mock
    assert saved_app.advocacy_materials[0] == mock_gcs_obj_ref["key"]

    # Verify GCSObjectReference was instantiated
    assert mock_gcs_obj_ref["cls"].call_count > 0
    # We can't verify 'get' on the key because it's a mock, but we know put() was called on the instance
    assert mock_gcs_obj_ref["instance"].put.called
    assert mock_gcs_obj_ref["instance"].filename == "test.pdf"
    assert mock_gcs_obj_ref["instance"].bucket_name == "test-bucket"

def test_upload_activities_advocacy_too_many(client, login, mock_user, mock_gcs, mock_gcs_obj_ref):
    # Fill up materials with mock keys
    refs = [MagicMock() for _ in range(MAX_ADVOCACY_ITEMS)]
    mock_user.application.get.return_value.advocacy_materials = refs

    data = {
        "upload_file": (BytesIO(b"test content"), "extra.pdf")
    }
    response = client.post(
        "/application/upload/activities/advocacy",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"Cannot upload more than" in response.data

def test_upload_no_file(client, login, mock_user):
    response = client.post(
        "/application/upload/activities/advocacy",
        data={},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"No files were found" in response.data

def test_upload_activities_newsletter(client, login, mock_user, mock_gcs, mock_gcs_obj_ref):
    mock_user.application.get.return_value.newsletter_materials = []
    data = {
        "upload_file": (BytesIO(b"newsletter"), "news.pdf")
    }
    response = client.post(
        "/application/upload/activities/newsletter",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200

    saved_app = mock_user.application.get.return_value
    assert len(saved_app.newsletter_materials) == 1
    assert saved_app.newsletter_materials[0] == mock_gcs_obj_ref["key"]

def test_upload_other_materials(client, login, mock_user, mock_gcs, mock_gcs_obj_ref):
    mock_user.application.get.return_value.other_materials = []
    data = {
        "upload_file": (BytesIO(b"other"), "other.pdf")
    }
    response = client.post(
        "/application/upload/other",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200

    saved_app = mock_user.application.get.return_value
    assert len(saved_app.other_materials) == 1
    assert saved_app.other_materials[0] == mock_gcs_obj_ref["key"]

def test_upload_file_too_large(client, login, mock_user, mock_gcs):
    # Patch the constant to be very small so our "fake" content triggers the limit
    with patch("dkc.application.files_upload.MAX_ADVOCACY_UPLOAD_SIZE_BYTES", 1):
        data = {
            "upload_file": (BytesIO(b"fake"), "large.pdf")
        }
        response = client.post(
            "/application/upload/activities/advocacy",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 413
        assert b"is too large" in response.data

def test_delete_file_success(client, login, mock_user, mock_gcs):
    # Setup: Create a file key and add to application
    # We need to ensure that the key passed in URL can resolve to a GCSObjectReference

    # Explicitly setup mock application key and entity to ensure equality checks pass
    mock_app_key = MagicMock(name="APP_KEY")
    mock_app_entity = MagicMock(name="APP_ENTITY")
    mock_app_key.get.return_value = mock_app_entity

    mock_user.application = mock_app_key

    # Mock the Key.get() call inside delete_file to return our GCSObjectReference mock
    mock_ref_instance = MagicMock(spec=GCSObjectReference)

    # Create the key that represents the file
    ref_key = MagicMock()
    ref_key.urlsafe.return_value = b"safe_key"
    ref_key.parent.return_value = mock_app_key # Configure parent match

    # Assign this key to the object reference
    mock_ref_instance.key = ref_key
    mock_ref_instance.bucket_name = "test-bucket"
    mock_ref_instance.object_name = "obj"

    with patch("google.cloud.ndb.Key") as mock_key_cls:
        # returns the key instance from URL
        key_instance = MagicMock()
        key_instance.get.return_value = mock_ref_instance
        mock_key_cls.return_value = key_instance

        # Add this key to the application materials list
        mock_app_entity.advocacy_materials = [ref_key]


        # Patch remove_file_from_application to avoid transactional wrapper causing RetryError with mock NDB
        def fake_remove(app_key, ref_key):
            app = app_key.get()
            if ref_key in app.advocacy_materials:
                app.advocacy_materials.remove(ref_key)

        with patch("dkc.application.files_delete.remove_file_from_application", side_effect=fake_remove) as mock_remove:
            url = f"/application/delete/f/safe_key"
            response = client.post(url)

            assert response.status_code == 204

            # Verify removed from application
            assert len(mock_app_entity.advocacy_materials) == 0

            # Verify call
            assert mock_remove.called

        # Verify GCS deletion called
        assert mock_gcs['blob'].delete.called

def test_delete_file_forbidden(client, login, mock_user, mock_gcs):
    # Setup mock content to belong to another
    mock_ref_instance = MagicMock(spec=GCSObjectReference)
    # Parent is distinct from user app
    mock_ref_instance.key.parent.return_value = MagicMock()

    with patch("google.cloud.ndb.Key") as mock_key_cls:
        key_instance = MagicMock()
        key_instance.get.return_value = mock_ref_instance
        mock_key_cls.return_value = key_instance

        url = "/application/delete/f/safe_key"
        response = client.post(url)

    assert response.status_code == 403

def test_delete_file_invalid_key(client, login, mock_user):
    url = "/application/delete/f/invalid-key"
    response = client.post(url)
    assert response.status_code == 400
