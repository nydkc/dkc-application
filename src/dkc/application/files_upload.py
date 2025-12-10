import logging
import os
import json
from flask import abort, request
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from google.cloud import exceptions, ndb, storage
from common.gcs import gcs
from common.jinja_functions import toFileInfo, byteConversion
from common.models import Settings
from .models import GCSObjectReference
from . import application_bp

logger = logging.getLogger(__name__)

MAX_ADVOCACY_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_ADVOCACY_ITEMS = 5
MAX_NEWSLETTER_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_NEWSLETTER_ITEMS = 5
MAX_OTHER_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024
MAX_OTHER_ITEMS = 3


@application_bp.route("/upload/activities/advocacy", methods=["GET", "POST"])
@login_required
def upload_activities_advocacy():
    if request.method == "GET":
        return get_upload_link(request.url)
    else:
        # Even if we don't use this value now, we need Flask to consume the
        # users' request files, otherwise they'll get a connection reset error
        # (because their file content was not read by the server), if we abort
        # the request.
        upload_files = request.files.getlist("upload_file")
        return handle_activities_advocacy_post()


def handle_activities_advocacy_post():
    applicant = current_user
    application = applicant.application.get()

    if application.submit_time:
        logger.warning(
            "Attempt to upload advocacy material by %s after submission",
            applicant.email,
        )
        return abort(
            409,
            description="Cannot upload materials for an already submitted application.",
        )
    if len(application.advocacy_materials) >= MAX_ADVOCACY_ITEMS:
        return abort(
            400,
            description=f"Cannot upload more than {MAX_ADVOCACY_ITEMS} advocacy materials.",
        )

    new_gcs_obj_ref_key = handle_upload_file(
        applicant, application, MAX_ADVOCACY_UPLOAD_SIZE_BYTES
    )
    if not application.advocacy_materials:
        application.advocacy_materials = []
    application.advocacy_materials.append(new_gcs_obj_ref_key)
    application.put()

    return json.dumps(toFileInfo([new_gcs_obj_ref_key]))


@application_bp.route("/upload/activities/newsletter", methods=["GET", "POST"])
@login_required
def upload_activities_newsletter():
    if request.method == "GET":
        return get_upload_link(request.url)
    else:
        # Even if we don't use this value now, we need Flask to consume the
        # users' request files, otherwise they'll get a connection reset error
        # (because their file content was not read by the server), if we abort
        # the request.
        upload_files = request.files.getlist("upload_file")
        return handle_activities_newsletter_post()


def handle_activities_newsletter_post():
    applicant = current_user
    application = applicant.application.get()

    if application.submit_time:
        logger.warning(
            "Attempt to upload newsletter material by %s after submission",
            applicant.email,
        )
        return abort(
            409,
            description="Cannot upload materials for an already submitted application.",
        )
    if len(application.newsletter_materials) >= MAX_NEWSLETTER_ITEMS:
        return abort(
            400,
            description=f"Cannot upload more than {MAX_NEWSLETTER_ITEMS} newsletter materials.",
        )

    new_gcs_obj_ref_key = handle_upload_file(
        applicant, application, MAX_NEWSLETTER_UPLOAD_SIZE_BYTES
    )
    if not application.newsletter_materials:
        application.newsletter_materials = []
    application.newsletter_materials.append(new_gcs_obj_ref_key)
    application.put()

    return json.dumps(toFileInfo([new_gcs_obj_ref_key]))


@application_bp.route("/upload/other", methods=["GET", "POST"])
@login_required
def upload_other():
    if request.method == "GET":
        return get_upload_link(request.url)
    else:
        # Even if we don't use this value now, we need Flask to consume the
        # users' request files, otherwise they'll get a connection reset error
        # (because their file content was not read by the server), if we abort
        # the request.
        upload_files = request.files.getlist("upload_file")
        return handle_activities_other_post()


def handle_activities_other_post():
    applicant = current_user
    application = applicant.application.get()

    if application.submit_time:
        logger.warning(
            "Attempt to upload other material by %s after submission",
            applicant.email,
        )
        return abort(
            409,
            description="Cannot upload materials for an already submitted application.",
        )
    if len(application.other_materials) >= MAX_OTHER_ITEMS:
        return abort(
            400,
            description=f"Cannot upload more than {MAX_OTHER_ITEMS} other materials.",
        )

    new_gcs_obj_ref_key = handle_upload_file(
        applicant, application, MAX_OTHER_UPLOAD_SIZE_BYTES
    )
    if not application.other_materials:
        application.other_materials = []
    application.other_materials.append(new_gcs_obj_ref_key)
    application.put()

    return json.dumps(toFileInfo([new_gcs_obj_ref_key]))


def get_upload_link(redirect_uri):
    # Historical reasons required the frontend to request an upload link for
    # direct uploads to Blobstore. This is now replaced by the AppEngine app
    # proxying the bytes to GCS.
    return redirect_uri


def handle_upload_file(applicant, application, max_size_bytes):
    upload_files = request.files.getlist("upload_file")
    if len(upload_files) == 0:
        abort(400, description="No files were found in your request")
    elif len(upload_files) > 1:
        abort(400, description="Only one file can be uploaded at a time")
    # We only accept one file upload at a time
    upload_file = upload_files[0]

    upload_file.seek(0, os.SEEK_END)
    upload_file_size = upload_file.tell()
    upload_file.seek(0)
    logger.info(
        "Uploading file '%s' from %s of size %s",
        upload_file.filename,
        applicant.email,
        upload_file_size,
    )
    if upload_file_size > max_size_bytes:
        return abort(
            413,
            description=f"File '{upload_file.filename}' is too large. Its size of {byteConversion(upload_file_size)} is over the limit of {byteConversion(max_size_bytes)}",
        )

    settings = Settings.get_config()
    bucket = gcs.get_bucket(settings.gcs_bucket)
    key = GCSObjectReference.allocate_ids(parent=application.key, size=1)[0]
    obj_name = "uploads/{}/{}/{}".format(
        settings.due_date.strftime("%Y"),
        key.urlsafe().decode("utf-8"),
        upload_file.filename,
    )
    obj = storage.Blob(obj_name, bucket)
    try:
        obj.upload_from_file(
            upload_file.stream,
            size=upload_file_size,
            content_type=upload_file.content_type,
        )
    except exceptions.GoogleCloudError as e:
        logger.error(
            "Encountered an error while uploading file from %s to GCS: %s",
            applicant.email,
            obj.name,
        )
        raise
    obj.reload()

    obj_ref = GCSObjectReference(
        key=key,
        bucket_name=bucket.name,
        object_name=obj.name,
        filename=upload_file.filename,
        content_type=obj.content_type,
        bytes_size=obj.size,
    )
    obj_ref_key = obj_ref.put()
    return obj_ref_key
