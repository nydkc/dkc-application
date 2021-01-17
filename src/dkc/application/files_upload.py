import logging
import os
import urllib.parse
import json
from flask import abort, request
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from google.cloud import exceptions, ndb, storage
from common.jinja_functions import toFileInfo, byteConversion
from common.models import Settings
from .models import GCSObjectReference
from . import application_bp

gcs = storage.Client()

MAX_ADVOCACY_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_NEWSLETTER_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024


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
        logging.info(
            "Attempt to upload advocacy material by %s after submission",
            applicant.email,
        )
        return abort(
            400,
            description="Cannot upload materials for an already submitted application.",
        )
    if len(application.advocacy_materials) >= 5:
        return abort(400, description="Cannot upload more than 5 advocacy materials.")

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
        logging.info(
            "Attempt to upload newsletter material by %s after submission",
            applicant.email,
        )
        return abort(
            400,
            description="Cannot upload materials for an already submitted application.",
        )
    if len(application.newsletter_materials) >= 5:
        return abort(400, description="Cannot upload more than 5 newsletter materials.")

    new_gcs_obj_ref_key = handle_upload_file(
        applicant, application, MAX_NEWSLETTER_UPLOAD_SIZE_BYTES
    )
    if not application.newsletter_materials:
        application.newsletter_materials = []
    application.newsletter_materials.append(new_gcs_obj_ref_key)
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
    logging.info(
        "Uploading file '%s' from %s of size %s",
        upload_file.filename,
        applicant.email,
        upload_file_size,
    )
    if upload_file_size > max_size_bytes:
        return abort(
            413,
            description="File '{}' is too large. Its size of {} is over the limit of {}".format(
                upload_file.filename,
                byteConversion(upload_file_size),
                byteConversion(max_size_bytes),
            ),
        )

    settings = ndb.Key(Settings, "config").get()
    bucket = gcs.get_bucket(settings.gcs_bucket)
    key = GCSObjectReference.allocate_ids(parent=application.key, size=1)[0]
    obj_name = "uploads/{}/{}-{}".format(
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
        logging.error(
            "Encountered an error while uploading file from %s to GCS: %s",
            applicant.email,
            obj.id,
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


# class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):

#     def get(self, resource):
#         resource = str(urllib.unquote(resource))
#         blob_info = blobstore.BlobInfo.get(resource)
#         if blob_info is None:
#             self.abort(404)
#             return

#         if "image" in blob_info.content_type:
#             image_url = images.get_serving_url(resource) + "=s0"
#             self.redirect(image_url)
#         else:
#             self.send_blob(blob_info)

# class DeleteHandler(BaseHandler):

#     @user_required
#     def get(self, resource):
#         resource = str(urllib.unquote(resource))
#         blob_info = blobstore.BlobInfo.get(resource)
#         if blob_info is None:
#             self.abort(404)
#             return

#         applicant = self.user
#         application_key = applicant.application
#         application = application_key.get()

#         if resource in application.other_materials:
#             application.other_materials.remove(resource)
#         elif resource in application.advocacy_materials:
#             application.advocacy_materials.remove(resource)
#             self.redirect('/application/activities')
#         # Users should not know about files that are not part of their application
#         else:
#             self.abort(404)
#             return
#         application.put()
#         deleted = DeletedFile(parent=self.user.key, user=self.user.key, blob=blob_info.key())
#         deleted.put()

#         self.response.write("Delete Successful: %s" % resource)
